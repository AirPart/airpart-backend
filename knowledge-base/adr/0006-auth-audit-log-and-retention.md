# ADR 0006 — Store authentication audit events in an append-only database table

- **Status:** Proposed
- **Date:** 2026-11-21
- **Decision owner:** Mohammad Hosein Ajorloo (backend lead) / Mohammad Hosein Ajorloo (security lead)
- **Scope:** Authentication layer, persistence, admin/API access, data retention
- **Related issue:** https://github.com/AirPart/airpart-backend/issues/90
- **Supersedes:** —

---

## 1. Context

The ERP handles authentication for staff who can move money, approve invoices and
assign roles. Today a successful or failed login, a password change or a role
assignment leaves no durable trace beyond framework logs, which are rotated and
not queryable by event.

Security review and the parent issue require four events to be recorded with a
timestamp and, when available, IP address and User-Agent: `login_success`,
`login_failed`, `password_changed`, `role_assigned`. Passwords, password hashes
and full access/refresh tokens must never reach the audit store. Records must be
readable only by explicitly authorised users, and retention must be at least
90 days.

Constraints:

- The backend is Django 5.2 LTS on PostgreSQL (see ADR-0002, ADR-0003).
- The auth path is latency-sensitive; audit writes must not add noticeable delay.
- The team is small; a new always-on infrastructure component is expensive.
- Redaction must be enforced in one place, not re-implemented per call site.

## 2. Decision Drivers

| #   | Driver                                  | Weight | Why it matters                                                  |
| --- | --------------------------------------- | ------ | --------------------------------------------------------------- |
| D1  | Queryability and review workflow        | 5      | Investigators must filter by user, event and time range quickly |
| D2  | Redaction and data-minimisation control | 5      | A single leak of a token defeats the purpose of the feature     |
| D3  | Tamper resistance / integrity           | 4      | Audit evidence is worthless if it can be silently edited        |
| D4  | Integration and maintenance effort      | 3      | Small team; every extra component has an ongoing cost           |
| D5  | Performance impact on the auth path     | 3      | Login latency is user-visible and must stay low                 |
| D6  | Retention, purge and archival control   | 4      | The 90-day policy must be enforceable and auditable             |
| D7  | Operational cost and dependencies       | 2      | Fewer moving parts is better, but not at the cost of D1–D3      |

## 3. Options Considered

### Option A — Dedicated append-only table in the primary database

A Django model `AuthAuditLog` in the auth app, written only through a service
layer that redacts sensitive keys before insert. Read-only Django Admin and a
permission-gated DRF endpoint for viewing. A scheduled management command purges
records older than the retention window.

- **Strengths:** native filtering and indexing; transactional with the user
  action; redaction centralised in one service; no new infrastructure; purge and
  archival are plain SQL/ORM operations.
- **Weaknesses:** shares the database with business data, so a DB administrator
  can alter records; no built-in WORM guarantee; table growth needs monitoring.
- **Official documentation:** https://docs.djangoproject.com/en/5.2/ref/models/fields/#jsonfield

### Option B — Structured application logs shipped to an external SIEM

Emit JSON lines through Python `logging` and forward them to an external log
platform (e.g. Elastic/OpenSearch, Loki, a managed SIEM).

- **Strengths:** strong tamper resistance when shipped off-host; excellent
  full-text search; independent retention configuration; no DB growth.
- **Weaknesses:** requires new infrastructure and credentials; redaction must be
  enforced in a logging filter and is easy to bypass; no transactional coupling
  with the user action; local querying for the admin UI needs a second API.
- **Official documentation:** https://docs.python.org/3/library/logging.html

### Option C — Third-party audit package (django-auditlog / django-simple-history)

Adopt a generic model-history library and configure it for the auth models.

- **Strengths:** very little code; proven migration path; captures field-level
  diffs automatically.
- **Weaknesses:** designed for change history, not security events; redaction of
  arbitrary payloads is not a first-class feature; schema is coupled to the
  library's migrations; custom event types (e.g. `login_failed` for a
  non-existent user) do not fit the model cleanly.
- **Official documentation:** https://django-auditlog.readthedocs.io/

## 4. Comparison

Scores are 1–5 (5 = best). Weighted score = score × weight.

| Criterion                             | Weight | A       | B      | C      |
| ------------------------------------- | ------ | ------- | ------ | ------ |
| D1 Queryability and review workflow   | 5      | 5 → 25  | 3 → 15 | 4 → 20 |
| D2 Redaction control                  | 5      | 5 → 25  | 4 → 20 | 3 → 15 |
| D3 Tamper resistance / integrity      | 4      | 3 → 12  | 5 → 20 | 2 → 8  |
| D4 Integration and maintenance effort | 3      | 4 → 12  | 3 → 9  | 5 → 15 |
| D5 Performance impact on auth path    | 3      | 4 → 12  | 5 → 15 | 4 → 12 |
| D6 Retention and purge control        | 4      | 5 → 20  | 3 → 12 | 2 → 8  |
| D7 Operational cost and dependencies  | 2      | 5 → 10  | 2 → 4  | 4 → 8  |
| **Weighted total (max 130)**          | **26** | **116** | **95** | **86** |

Option A wins on the two heaviest drivers (queryability and redaction control)
and on retention, and is only beaten on tamper resistance, which is mitigated in
section 6.

## 5. Decision

Authentication audit events are stored in a dedicated append-only table in the
primary PostgreSQL database, written exclusively through a redacting service
layer.

1. **Schema.** `AuthAuditLog` with `event_type` (choices: `login_success`,
   `login_failed`, `password_changed`, `role_assigned`), `user` (nullable FK,
   `on_delete=SET_NULL` so history survives user deletion), `timestamp`
   (`auto_now_add`), `ip_address` (nullable `GenericIPAddressField`),
   `user_agent` (nullable text) and `metadata` (`JSONField`, default `dict`).
   Composite indexes on `(event_type, timestamp)` and `(user, timestamp)`.
2. **Write path.** A single service, `record_auth_event(...)`, is the only
   permitted writer. It extracts IP and User-Agent from the request, recursively
   redacts any key matching `password`, `token`, `secret`, `authorization`,
   `access`, `refresh` (case-insensitive, including nested dicts and lists) to
   `"[REDACTED]"`, and never accepts raw `User`/`request` objects in metadata.
   A logging failure must never break the originating request.
3. **Read path.** Django Admin is read-only (no add/change/delete). The DRF
   endpoint is read-only, paginated and requires an explicit permission
   (`view_auth_audit_log` or `IsAdminUser`).
4. **Retention.** Records are kept for at least 90 days. A scheduled management
   command deletes records older than the configured window (default 90 days);
   the policy is documented in `docs/security/audit-retention.md`.
5. **Integrity.** Application code never updates or deletes rows outside the
   purge command; database-level `UPDATE`/`DELETE` grants for the app role are
   narrowed where the deployment allows it.

## 6. Consequences

### Positive

- Investigators can answer "who logged in from where, and when" with an indexed
  query, without new infrastructure.
- Redaction lives in exactly one function and is covered by negative tests.
- Retention is enforceable with a single command and a documented policy.
- Audit rows are written in the same transaction context as the user action.

### Negative / Risks

- A database administrator can still modify rows; the table is not WORM.
- The table grows indefinitely within the retention window and needs monitoring.
- Synchronous writes add a small amount of latency to login.
- A purge bug could delete evidence prematurely.

### Mitigations

- Restrict production DB credentials; consider streaming a copy to external
  storage later (this is the review trigger for Option B).
- Indexes plus a purge job keep the hot set bounded; monitor row count and size.
- Wrap audit writes so failures are logged and swallowed, never propagated.
- The purge command defaults to a dry-run flag and is covered by tests for the
  89/91-day boundary.

## 7. Rejected Options

| Option                        | Reason for rejection                                                                                                                                                |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| B — External SIEM             | Failed D2 (redaction is easy to bypass in a logging filter) and D4/D7 (new infrastructure and credentials), despite winning D3.                                     |
| C — Third-party audit package | Failed D2 (no first-class payload redaction) and D6 (retention tied to library schema), and its change-history model does not fit `login_failed` for unknown users. |

## 8. Proof of Concept / Validation

- **Branch:** `100-feat/auth-audit-log-model`
- **Scope of the PoC:** model + migration + service redaction + one integration
  test per event type.
- **Acceptance criteria:** four events persisted with timestamp/IP/User-Agent;
  injected `password`/`access_token` absent from the serialised row; unauthorised
  API access returns 403; purge removes a 91-day-old row and keeps an 89-day-old
  one.
- **Evidence:** <link to CI run / test output>

## 9. References

- Django 5.2 `JSONField`: https://docs.djangoproject.com/en/5.2/ref/models/fields/#jsonfield
- Django 5.2 `GenericIPAddressField`: https://docs.djangoproject.com/en/5.2/ref/models/fields/#genericipaddressfield
- Django auth signals (`user_logged_in`, `user_login_failed`, `password_changed`): https://docs.djangoproject.com/en/5.2/ref/contrib/auth/#module-django.contrib.auth.signals
- Django logging: https://docs.djangoproject.com/en/5.2/topics/logging/
- OWASP Logging Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html
- NIST SP 800-92, Guide to Computer Security Log Management: https://csrc.nist.gov/pubs/sp/800/92/final
- django-auditlog: https://django-auditlog.readthedocs.io/
- django-simple-history: https://django-simple-history.readthedocs.io/

## 10. Review Trigger

Reopen this decision if any of the following becomes true:

- p95 latency added by the audit write exceeds 20 ms in staging.
- Audit rows exceed 5 million per year, or the table exceeds 10% of database size.
- A compliance requirement demands WORM storage or off-host immutable copies.
- Multi-tenant/branch isolation requires audit rows to be partitioned per tenant.
- The primary database is split or migrated to a separate cluster.
