"""The only supported way to write to the authentication audit log."""

import ipaddress
import json
import logging

from django.conf import settings
from django.core.exceptions import ValidationError

from app.accounts.models import AuthAuditLog

from .redaction import redact

logger = logging.getLogger(__name__)

MAX_USER_AGENT = 512
MAX_METADATA_BYTES = 8 * 1024


def _trusted_proxy_count() -> int:
    return int(getattr(settings, "AUDIT_TRUSTED_PROXY_COUNT", 0))


def _parse_ip(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        return str(ipaddress.ip_address(raw.strip()))
    except ValueError:
        return None

def _client_ip(request) -> str | None:
    remote_addr = request.META.get("REMOTE_ADDR")
    count = max(int(getattr(settings, "AUDIT_TRUSTED_PROXY_COUNT", 0)), 0)

    if count <= 0:
        return _parse_ip(remote_addr)

    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    hops = [hop.strip() for hop in forwarded.split(",") if hop.strip()]

    # If we have trusted proxies, the client IP is located to the left of our trusted hops.
    # Right-most hops correspond to trusted proxies.
    index = len(hops) - count - 1
    if 0 <= index < len(hops):
        return _parse_ip(hops[index])

    return _parse_ip(remote_addr)

def extract_client_info(request) -> tuple[str | None, str]:
    """Return ``(ip_address, user_agent)`` for a request."""
    user_agent = (request.META.get("HTTP_USER_AGENT") or "")[:MAX_USER_AGENT]
    return _client_ip(request), user_agent


def _json_safe(value):
    """Convert arbitrary metadata to JSON-serialisable values."""
    try:
        json.dumps(value)
        return value
    except (TypeError, ValueError):
        return json.loads(json.dumps(value, default=str))


def _build_metadata(metadata: dict) -> dict:
    cleaned = redact(_json_safe(metadata))
    if len(json.dumps(cleaned)) > MAX_METADATA_BYTES:
        return {"truncated": True}
    return cleaned


def record_auth_event(
    event_type: str,
    request=None,
    user=None,
    **metadata,
) -> AuthAuditLog | None:
    """Persist one audit event. Never raises; returns None on failure."""
    try:
        ip_address, user_agent = (None, "")
        if request is not None:
            ip_address, user_agent = extract_client_info(request)
            if user is None:
                candidate = getattr(request, "user", None)
                if candidate is not None and candidate.is_authenticated:
                    user = candidate

        return AuthAuditLog.objects.create(
            event_type=event_type,
            user=user,
            ip_address=ip_address,
            user_agent=user_agent or None,
            metadata=_build_metadata(metadata),
        )
    except Exception:
        logger.exception("Failed to record auth audit event %r", event_type)
        if getattr(settings, "AUDIT_LOG_STRICT", False):
            raise
        return None
