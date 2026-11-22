"""Audit hooks for session-based authentication (the Django admin).

The JWT path is audited in ``AuditedTokenObtainPairSerializer``. These
receivers cover ``/admin/login/``, which never touches that serializer.

``user_login_failed`` also fires for the JWT path, because simplejwt calls
``django.contrib.auth.authenticate()``. The path guard below prevents a
duplicate ``login_failed`` row for ``/api/auth/login``.
"""

from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver

from app.accounts.models import AuthAuditLog
from app.accounts.services import record_auth_event

JWT_LOGIN_PATH = "/api/auth/login"


def _is_jwt_login(request) -> bool:
    path = getattr(request, "path", "") or ""
    return path.rstrip("/") == JWT_LOGIN_PATH


@receiver(user_logged_in)
def audit_session_login_success(sender, request, user, **kwargs):
    record_auth_event(
        AuthAuditLog.EventType.LOGIN_SUCCESS,
        request=request,
        user=user,
        method="session",
        domain=getattr(user, "domain", ""),
    )


@receiver(user_login_failed)
def audit_login_failure(sender, credentials, request=None, **kwargs):
    if request is not None and _is_jwt_login(request):
        return
    record_auth_event(
        AuthAuditLog.EventType.LOGIN_FAILED,
        request=request,
        username=credentials.get("username", ""),
        reason="invalid_credentials",
    )
