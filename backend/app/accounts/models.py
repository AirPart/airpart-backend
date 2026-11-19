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
