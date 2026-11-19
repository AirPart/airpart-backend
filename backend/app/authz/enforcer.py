"""Thin wrapper around Casbin.

The enforcer is cached for the lifetime of the process. Policy changes made on
disk require a process restart (or ``get_enforcer.cache_clear()``); this is
acceptable for the PoC but must be revisited when policies become dynamic.
"""

from functools import lru_cache

import casbin
from django.conf import settings


@lru_cache(maxsize=1)
def get_enforcer() -> casbin.Enforcer:
    return casbin.Enforcer(
        str(settings.CASBIN_MODEL_PATH), str(settings.CASBIN_POLICY_PATH)
    )


def is_allowed(user, obj: str, act: str) -> bool:
    """Evaluate ``user`` against the policy for ``obj``/``act``."""
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    if user.is_superuser:
        return True
    return bool(get_enforcer().enforce(user.username, user.domain, obj, act))
