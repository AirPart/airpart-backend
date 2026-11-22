"""Integration tests: login events reach the audit table."""

import json

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher

from app.accounts.models import AuthAuditLog

from .conftest import PASSWORD, login

User = get_user_model()

EventType = AuthAuditLog.EventType

UNIQUE_PASSWORD = "Str0ng!Uniq-9f3a2b"


@pytest.fixture
def carol(db):
    return User.objects.create_user(
        username="carol",
        password=UNIQUE_PASSWORD,
        role=User.Role.SALES,
        domain="branch_tehran",
    )


def _events(event_type):
    return AuthAuditLog.objects.filter(event_type=event_type)


# --------------------------------------------------------------------------
# login_success
# --------------------------------------------------------------------------


def test_successful_login_records_one_event(
    api_client, alice, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "alice")

    assert _events(EventType.LOGIN_SUCCESS).count() == 1


def test_successful_login_event_has_expected_fields(
    api_client, alice, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "alice")

    event = _events(EventType.LOGIN_SUCCESS).get()

    assert event.user == alice
    assert event.ip_address == "127.0.0.1"
    assert event.metadata["method"] == "jwt"
    assert event.metadata["domain"] == "branch_tehran"


def test_successful_login_does_not_record_a_failure(
    api_client, alice, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "alice")

    assert _events(EventType.LOGIN_SUCCESS).count() == 1
    assert not _events(EventType.LOGIN_FAILED).exists()


# --------------------------------------------------------------------------
# login_failed
# --------------------------------------------------------------------------


def test_failed_login_records_one_event(api_client, alice):
    login(api_client, "alice", password="wrong-password")

    assert _events(EventType.LOGIN_FAILED).count() == 1


def test_failed_login_event_has_expected_fields(api_client, alice):
    login(api_client, "alice", password="wrong-password")

    event = _events(EventType.LOGIN_FAILED).get()

    assert event.user is None
    assert event.metadata["username"] == "alice"
    assert event.metadata["reason"] == "invalid_credentials"


def test_failed_login_does_not_record_a_success(api_client, alice):
    login(api_client, "alice", password="wrong-password")

    assert _events(EventType.LOGIN_FAILED).count() == 1
    assert not _events(EventType.LOGIN_SUCCESS).exists()


def test_failed_login_for_unknown_user_is_recorded(api_client, db):
    login(api_client, "nobody-here", password="wrong-password")

    event = _events(EventType.LOGIN_FAILED).get()

    assert event.user is None
    assert event.metadata["username"] == "nobody-here"


def test_incomplete_payload_records_nothing(api_client, db):
    api_client.post("/api/auth/login", {"username": "alice"}, format="json")

    assert not AuthAuditLog.objects.exists()


# --------------------------------------------------------------------------
# Admin (session) path
# --------------------------------------------------------------------------


def test_admin_login_records_a_session_event(client, alice):
    alice.is_staff = True
    alice.is_superuser = True
    alice.save()

    client.post(
        "/admin/login/",
        {"username": "alice", "password": PASSWORD, "next": "/admin/"},
    )

    event = _events(EventType.LOGIN_SUCCESS).get()

    assert event.user == alice
    assert event.metadata["method"] == "session"


def test_admin_failed_login_records_one_event(client, alice):
    alice.is_staff = True
    alice.save()

    client.post(
        "/admin/login/",
        {"username": "alice", "password": "wrong-password", "next": "/admin/"},
    )

    assert _events(EventType.LOGIN_FAILED).count() == 1


# --------------------------------------------------------------------------
# Password handling invariants
# --------------------------------------------------------------------------


def test_password_is_stored_hashed(
    api_client, carol, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "carol", password=UNIQUE_PASSWORD)

    carol.refresh_from_db()

    assert identify_hasher(carol.password) is not None
    assert UNIQUE_PASSWORD not in carol.password


def test_login_does_not_modify_the_stored_credential(
    api_client, carol, django_capture_on_commit_callbacks
):
    before = carol.password

    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "carol", password=UNIQUE_PASSWORD)

    carol.refresh_from_db()

    assert carol.password == before


def test_stored_credential_still_validates_after_login(
    api_client, carol, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "carol", password=UNIQUE_PASSWORD)

    carol.refresh_from_db()

    assert carol.check_password(UNIQUE_PASSWORD)


def test_failed_login_does_not_modify_the_stored_credential(api_client, carol):
    before = carol.password

    login(api_client, "carol", password="wrong-password")

    carol.refresh_from_db()

    assert carol.password == before
    assert carol.check_password(UNIQUE_PASSWORD)


def test_no_password_material_reaches_the_audit_table(
    api_client, carol, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        login(api_client, "carol", password=UNIQUE_PASSWORD)

    login(api_client, "carol", password="wrong-password")

    dumped = json.dumps(list(AuthAuditLog.objects.values()), default=str)

    assert UNIQUE_PASSWORD not in dumped
    assert "wrong-password" not in dumped
    assert carol.password not in dumped
