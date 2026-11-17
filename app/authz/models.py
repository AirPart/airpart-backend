import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db import models

class TimeStampedAuditModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at', 'updated_at'])

class Role(TimeStampedAuditModel):

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class Permission(TimeStampedAuditModel):

    code = models.CharField(
        max_length=150, unique=True, help_text='Unique permission code e.g. parts:create'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return self.code


class UserRole(TimeStampedAuditModel):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_roles'
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')

    class Meta:
        db_table = 'user_roles'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'role'], name='unique_user_role'
            )
        ]

class RolePermission(TimeStampedAuditModel):

    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name='permission_roles'
    )

    class Meta:
        db_table = 'role_permissions'
        constraints = [
            models.UniqueConstraint(
                fields=['role', 'permission'], name='unique_role_permission'
            )
        ]
