import pytest

from .conftest import PASSWORD, login


def test_login_returns_access_and_refresh(api_client, alice):
    response = login(api_client, "alice")

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


def test_login_with_wrong_password_is_rejected(api_client, alice):
    response = login(api_client, "alice", password="wrong-password")

    assert response.status_code == 401
    assert "access" not in response.data


def test_me_requires_authentication(api_client):
    response = api_client.get("/api/me")

    assert response.status_code == 401


def test_me_returns_current_user(api_client, alice):
    token = login(api_client, "alice").data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = api_client.get("/api/me")

    assert response.status_code == 200
    assert response.data["username"] == "alice"
    assert response.data["role"] == "sales"
    assert response.data["domain"] == "branch_tehran"


def test_refresh_returns_new_access_token(api_client, alice):
    refresh = login(api_client, "alice").data["refresh"]

    response = api_client.post("/api/auth/refresh", {"refresh": refresh}, format="json")

    assert response.status_code == 200
    assert "access" in response.data
