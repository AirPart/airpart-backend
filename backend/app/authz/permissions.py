from rest_framework.permissions import BasePermission

from .enforcer import is_allowed


class CasbinPermission(BasePermission):
    """DRF permission backed by Casbin.

    The view declares ``casbin_obj`` and (optionally) ``casbin_act``.
    When ``casbin_act`` is omitted, the HTTP method is used as the action.
    """

    message = "You do not have permission to perform this action."

    def has_permission(self, request, view) -> bool:
        obj = getattr(view, "casbin_obj", None)
        if obj is None:
            return True
        act = getattr(view, "casbin_act", request.method.lower())
        return is_allowed(request.user, obj, act)
