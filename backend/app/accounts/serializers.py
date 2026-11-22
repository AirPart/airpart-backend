"""Serializers for the authentication endpoints.

The audited login serializer is the only place that knows both *who*
authenticated and *why* authentication failed, so the audit events are
emitted here rather than inferred from the HTTP status code in the view.
"""

from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed as DRFAuthenticationFailed
from rest_framework_simplejwt.exceptions import AuthenticationFailed as JWTAuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from app.accounts.models import AuthAuditLog
from app.accounts.services import record_auth_event

# simplejwt raises its own AuthenticationFailed, which is not a subclass of
# DRF's. Catch both so a future version bump cannot silently disable auditing.
AUTHENTICATION_FAILURES = (DRFAuthenticationFailed, JWTAuthenticationFailed)


class AuditedTokenObtainPairSerializer(TokenObtainPairSerializer):
    """``TokenObtainPairSerializer`` that records login audit events.

    ``login_failed`` is written immediately: there is no transaction to wait
    for, and the row must survive even if the client aborts the response.

    ``login_success`` is deferred with ``transaction.on_commit`` so that an
    audit write can never roll back a successful login (ADR-0006 §5.2).
    """

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
        except AUTHENTICATION_FAILURES:
            record_auth_event(
                AuthAuditLog.EventType.LOGIN_FAILED,
                request=self.context.get("request"),
                username=attrs.get(self.username_field, ""),
                reason="invalid_credentials",
            )
            raise

        user = self.user
        request = self.context.get("request")
        transaction.on_commit(
            lambda: record_auth_event(
                AuthAuditLog.EventType.LOGIN_SUCCESS,
                request=request,
                user=user,
                method="jwt",
                domain=user.domain,
            )
        )
        return data
