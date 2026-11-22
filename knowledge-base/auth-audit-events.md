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
| `password_changed` | No runtime password-change path exists yet                       | #<issue> |
| `role_assigned`    | No runtime role-assignment path; role source of truth unresolved | #<issue> |

## Invariants

- Every write goes through `record_auth_event()`; application code never calls
  `AuthAuditLog.objects.create()` directly.
- A failed login stores the attempted username only if that user exists;
  otherwise a truncated SHA-256 digest of it.
- No password, password hash or token ever reaches `metadata`.
- An audit failure never breaks the originating request (fail-open unless
  `AUDIT_LOG_STRICT` is set).
