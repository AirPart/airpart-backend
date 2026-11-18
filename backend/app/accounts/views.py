from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authz.permissions import CasbinPermission


class LoginView(TokenObtainPairView):
    """POST /api/auth/login -> {"access": ..., "refresh": ...}"""


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
