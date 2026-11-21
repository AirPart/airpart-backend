"""Redaction of sensitive values before they reach the audit log."""

from collections.abc import Mapping

REDACTED = "[REDACTED]"

SENSITIVE_KEYS = frozenset(
    {
        "password",
        "new_password",
        "old_password",
        "token",
        "access",
        "refresh",
        "access_token",
        "refresh_token",
        "authorization",
        "password_hash",
    }
)

SENSITIVE_FRAGMENTS = ("token", "password", "secret")


def is_sensitive_key(key: object) -> bool:
    """Return True when a metadata key must never be persisted verbatim."""
    normalized = str(key).lower().replace("-", "_")
    if normalized in SENSITIVE_KEYS:
        return True
    return any(fragment in normalized for fragment in SENSITIVE_FRAGMENTS)


def redact(value: object) -> object:
    """Return a copy of ``value`` with every sensitive key replaced.

    Works recursively through mappings, lists, tuples and sets. The input
    is never mutated.
    """
    if isinstance(value, Mapping):
        return {
            key: REDACTED if is_sensitive_key(key) else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple, set, frozenset)):
        return [redact(item) for item in value]
    return value
