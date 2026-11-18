import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

PASSWORD = "test-pass-12345"


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def alice(db):
    """Sales user in branch_tehran: allowed to read invoices."""
    return User.objects.create_user(
        username="alice", password=PASSWORD, role=User.Role.SALES, domain="branch_tehran"
    )


@pytest.fixture
def bob(db):
    """Sales user in branch_isfahan: no invoice policy for that domain."""
    return User.objects.create_user(
        username="bob", password=PASSWORD, role=User.Role.SALES, domain="branch_isfahan"
    )


def login(client: APIClient, username: str, password: str = PASSWORD):
    return client.post(
        "/api/auth/login", {"username": username, "password": password}, format="json"
    )
