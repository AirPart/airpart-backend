from app.accounts.models import AuthAuditLog
from app.accounts.serializers import (
    AuditedTokenObtainPairSerializer,
    ChangePasswordSerializer,
)
from app.accounts.services.audit import record_auth_event
from app.authz.permissions import CasbinPermission
from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


class LoginView(TokenObtainPairView):
    """POST /api/auth/login -> {"access": ..., "refresh": ...}"""

    serializer_class = AuditedTokenObtainPairSerializer


class RefreshView(TokenRefreshView):
    """POST /api/auth/refresh -> {"access": ..., "refresh": ...}"""


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """GET /api/me -> the current user."""
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "domain": user.domain,
            "is_superuser": user.is_superuser,
        }
    )


class InvoiceListView(APIView):
    """GET /api/invoices -> invoices visible in the user's domain.

    The payload is a stub; the point of the endpoint is that access is decided
    by Casbin policy, not by view code.
    """

    permission_classes = [IsAuthenticated, CasbinPermission]
    casbin_obj = "invoice"
    casbin_act = "read"

    def get(self, request):
        return Response(
            {
                "domain": request.user.domain,
                "invoices": [],
            }
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            self._record_failed_attempt(request, serializer)
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        transaction.on_commit(
            lambda: record_auth_event(
                request=request,
                event_type=AuthAuditLog.EventType.PASSWORD_CHANGED,
                user=user,
                source="api",
            )
        )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @staticmethod
    def _record_failed_attempt(request, serializer):
        errors = serializer.errors
        provided_fields = request.data.keys()

        if not {"old_password", "new_password"}.issubset(provided_fields):
            return

        if "old_password" in errors:
            reason = "wrong_old_password"
        elif "new_password" in errors:
            reason = "invalid_new_password"
        else:
            return

        record_auth_event(
            request=request,
            event_type="password_change_failed",
            username=request.user.username,
            reason=reason,
        )
