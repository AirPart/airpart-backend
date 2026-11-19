import pytest

from app.authz.enforcer import get_enforcer, is_allowed

from .conftest import login


def test_policy_allows_sales_in_own_domain(alice):
    assert is_allowed(alice, "invoice", "read") is True


def test_policy_denies_sales_outside_own_domain(bob):
    assert is_allowed(bob, "invoice", "read") is False


def test_policy_denies_action_not_granted(alice):
    assert is_allowed(alice, "invoice", "approve") is False


def test_policy_denies_unknown_object(alice):
    assert is_allowed(alice, "payroll", "read") is False


def test_policy_file_is_loaded():
    enforcer = get_enforcer()
    assert enforcer.enforce("alice", "branch_tehran", "invoice", "read") is True
    assert enforcer.enforce("bob", "branch_isfahan", "invoice", "read") is False


def test_endpoint_allows_authorized_user(api_client, alice):
    token = login(api_client, "alice").data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = api_client.get("/api/invoices")

    assert response.status_code == 200
    assert response.data["domain"] == "branch_tehran"


def test_endpoint_returns_403_for_unauthorized_user(api_client, bob):
    token = login(api_client, "bob").data["access"]
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    response = api_client.get("/api/invoices")

    assert response.status_code == 403
