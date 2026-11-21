from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user.

    ``role`` and ``domain`` are the inputs to Casbin policy evaluation:
    the subject is the username, the domain is the branch/department.
    """

    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        SALES = "sales", "Sales"
        HR = "hr", "HR"
        FINANCE = "finance", "Finance"

    role = models.CharField(max_length=32, choices=Role.choices, default=Role.SALES)
    domain = models.CharField(max_length=64, default="branch_tehran")

    def __str__(self) -> str:
        return f"{self.username} ({self.role}@{self.domain})"

class AuthAuditLog(models.Model):
    """Immutable record of one authentication security event."""

    class EventType(models.TextChoices):
        LOGIN_SUCCESS = "login_success", "Login success"
        LOGIN_FAILED = "login_failed", "Login failed"
        PASSWORD_CHANGED = "password_changed", "Password changed"
        ROLE_ASSIGNED = "role_assigned", "Role assigned"

    event_type = models.CharField(max_length=32, choices=EventType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="auth_audit_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "auth_audit_logs"
        ordering = ("-timestamp",)
        indexes = [
            models.Index(fields=["event_type", "timestamp"], name="audit_event_ts_idx"),
            models.Index(fields=["user", "timestamp"], name="audit_user_ts_idx"),
        ]
        verbose_name = "authentication audit log"
        verbose_name_plural = "authentication audit logs"

    def __str__(self) -> str:
        actor = self.user_id or "anonymous"
        return f"{self.timestamp:%Y-%m-%d %H:%M:%S} {self.event_type} user={actor}"
