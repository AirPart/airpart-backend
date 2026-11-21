from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AuthAuditLog, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ERP access", {"fields": ("role", "domain")}),
    )
    list_display = ("username", "email", "role", "domain", "is_staff")
    list_filter = ("role", "domain", "is_staff")

@admin.register(AuthAuditLog)
class AuthAuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "event_type", "user", "ip_address")
    list_filter = ("event_type", "timestamp")
    search_fields = ("user__username", "ip_address")
    date_hierarchy = "timestamp"
    readonly_fields = (
        "event_type", "user", "timestamp", "ip_address", "user_agent", "metadata",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
