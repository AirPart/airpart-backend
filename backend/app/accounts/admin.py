from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("ERP access", {"fields": ("role", "domain")}),
    )
    list_display = ("username", "email", "role", "domain", "is_staff")
    list_filter = ("role", "domain", "is_staff")
