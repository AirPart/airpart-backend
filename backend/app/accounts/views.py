from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import status

from app.accounts.services.audit import record_auth_event
from app.accounts.serializers import ChangePasswordSerializer
from app.accounts.serializers import AuditedTokenObtainPairSerializer


from app.authz.permissions import CasbinPermission
from app.accounts.models import AuthAuditLog

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

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])

        # Deferred so a failed audit write can never roll back the password
        # change, and so no row is written for a change that never committed.
        transaction.on_commit(
            lambda: record_auth_event(
                AuthAuditLog.EventType.PASSWORD_CHANGED,
                request=request,
                user=user,
                source="api",
            )
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
