# Auth audit events — implementation map

Which audit events exist, where they are recorded, and which paths are
deliberately not covered. Companion to
[ADR-0006](./adr/0006-auth-audit-log-and-retention.md).

## Recorded events

| Event           | Trigger point                                 | File                          | Notes                                                                               |
| --------------- | --------------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------- |
| `login_success` | `AuditedTokenObtainPairSerializer.validate()` | `app/accounts/serializers.py` | JWT path. `user_logged_in` never fires here. Deferred with `transaction.on_commit`. |
| `login_success` | `audit_session_login_success` receiver        | `app/accounts/signals.py`     | Django admin / any `django.contrib.auth.login()` call.                              |
| `login_failed`  | `AuditedTokenObtainPairSerializer.validate()` | `app/accounts/serializers.py` | JWT path. Written immediately.                                                      |
| `login_failed`  | `audit_login_failure` receiver                | `app/accounts/signals.py`     | Fires for both paths; skips `/api/auth/login` to avoid a duplicate row.             |

## Not recorded (and why)

| Event              | Reason                                                           | Tracking |
| ------------------ | ---------------------------------------------------------------- | -------- |
| `password_changed` | `POST /api/auth/change-password`                                 | #114     |
| `role_assigned`    | No runtime role-assignment path; role source of truth unresolved | #115     |

### `password_changed`

Self-service password change. The row is written inside
`transaction.on_commit`, so it exists only if the change actually committed.

**Request**

```json
{ "old_password": "...", "new_password": "..." }
```

**Responses**

| Status | Body                                                  | Meaning                                                         |
| ------ | ----------------------------------------------------- | --------------------------------------------------------------- |
| `204`  | empty                                                 | password changed                                                |
| `400`  | `{"old_password": ["Incorrect password."]}`           | wrong current password                                          |
| `400`  | `{"new_password": ["This password is too short..."]}` | rejected by Django validators, or equal to the current password |
| `401`  | —                                                     | no or invalid access token                                      |

**`metadata`**

```json
{ "source": "api" }
```

Neither password value is ever passed to `record_auth_event`. The redaction
layer in `services/audit.py` is a safety net, not a licence to pass secrets.

### Known limitations of `password_changed`

1. **Existing tokens stay valid.** The access token in the caller's hand and
   any refresh token issued earlier keep working until they expire. Changing
   the password does not evict an attacker who already holds a token.
   Follow-up: `feat(auth): invalidate tokens on password change`.
2. **No rate limiting.** This endpoint is a password-guessing oracle for
   anyone holding a stolen access token. Follow-up:
   `feat(security): add rate limiting to auth endpoints`.
3. **Failed attempts are not audited.** A wrong `old_password` produces a
   `400` and no row. Follow-up:
   `feat(auth): audit failed password-change attempts` (high priority).

## Invariants

- Every write goes through `record_auth_event()`; application code never calls
  `AuthAuditLog.objects.create()` directly.
- A failed login stores the attempted username only if that user exists;
  otherwise a truncated SHA-256 digest of it.
- No password, password hash or token ever reaches `metadata`.
- An audit failure never breaks the originating request (fail-open unless
  `AUDIT_LOG_STRICT` is set).
