import json

import pytest
from app.accounts.models import AuthAuditLog
from app.tests.conftest import PASSWORD, UNIQUE_PASSWORD
from django.contrib.auth.hashers import identify_hasher
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

URL = "/api/auth/change-password"


@pytest.fixture
def client_for(alice):
    """Authenticated client built without calling /auth/login.

    Going through the login endpoint would write a ``login_success`` row and
    make every row-count assertion ambiguous.
    """
    client = APIClient()
    access = RefreshToken.for_user(alice).access_token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    return client


def _dump_table():
    return json.dumps(list(AuthAuditLog.objects.values()), default=str)


@pytest.mark.django_db
def test_change_password_returns_204(client_for, alice):
    response = client_for.post(
        URL, {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD}
    )
    assert response.status_code == 204
    assert response.content == b""


@pytest.mark.django_db
def test_change_password_writes_exactly_one_event(
    client_for, alice, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        client_for.post(
            URL, {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD}
        )

    rows = AuthAuditLog.objects.filter(
        user=alice, event_type=AuthAuditLog.EventType.PASSWORD_CHANGED
    )
    assert rows.count() == 1
    # Catches stray rows of any other type written along the way.
    assert AuthAuditLog.objects.count() == 1


@pytest.mark.django_db
def test_event_metadata_is_source_api(
    client_for, alice, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        client_for.post(
            URL, {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD}
        )

    row = AuthAuditLog.objects.get(event_type=AuthAuditLog.EventType.PASSWORD_CHANGED)
    assert row.metadata == {"source": "api"}
    assert row.user_id == alice.pk


@pytest.mark.django_db
def test_event_records_client_ip_and_user_agent(
    client_for, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        client_for.post(
            URL,
            {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD},
            HTTP_USER_AGENT="pytest-agent/1.0",
        )

    row = AuthAuditLog.objects.get(event_type=AuthAuditLog.EventType.PASSWORD_CHANGED)
    assert row.ip_address == "127.0.0.1"
    assert row.user_agent == "pytest-agent/1.0"


@pytest.mark.django_db
def test_no_plaintext_password_anywhere_in_table(
    client_for, django_capture_on_commit_callbacks
):
    with django_capture_on_commit_callbacks(execute=True):
        client_for.post(
            URL, {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD}
        )

    dumped = _dump_table()
    assert UNIQUE_PASSWORD not in dumped
    assert PASSWORD not in dumped


@pytest.mark.django_db
def test_password_hash_changes_and_new_password_validates(
    client_for, alice, django_capture_on_commit_callbacks
):
    before = alice.password
    assert identify_hasher(before).algorithm

    with django_capture_on_commit_callbacks(execute=True):
        client_for.post(
            URL, {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD}
        )

    alice.refresh_from_db()
    assert alice.password != before
    assert identify_hasher(alice.password).algorithm
    assert alice.check_password(UNIQUE_PASSWORD) is True
    assert alice.check_password(PASSWORD) is False


@pytest.mark.django_db
def test_wrong_old_password_returns_400_and_writes_no_row(client_for, alice):
    response = client_for.post(
        URL, {"old_password": "definitely-not-it", "new_password": UNIQUE_PASSWORD}
    )

    rows = AuthAuditLog.objects.filter(
        user=alice,
        event_type="password_change_failed",
    )

    assert response.status_code == 400
    assert "old_password" in response.json()
    assert rows.count() == 1
    assert rows.get().metadata["reason"] == "wrong_old_password"


@pytest.mark.django_db
def test_wrong_old_password_leaves_hash_untouched(client_for, alice):
    before = alice.password
    client_for.post(
        URL, {"old_password": "definitely-not-it", "new_password": UNIQUE_PASSWORD}
    )

    alice.refresh_from_db()
    assert alice.password == before
    assert alice.check_password(PASSWORD) is True


@pytest.mark.django_db
def test_new_password_equal_to_old_is_rejected(client_for, alice):
    response = client_for.post(
        URL, {"old_password": PASSWORD, "new_password": PASSWORD}
    )

    rows = AuthAuditLog.objects.filter(
        user=alice,
        event_type="password_change_failed",
    )

    assert response.status_code == 400
    assert "new_password" in response.json()
    assert rows.get().metadata["reason"] == "invalid_new_password"


@pytest.mark.django_db
def test_weak_new_password_is_rejected(client_for, alice):
    response = client_for.post(URL, {"old_password": PASSWORD, "new_password": "123"})

    rows = AuthAuditLog.objects.filter(
        user=alice,
        event_type="password_change_failed",
    )

    assert response.status_code == 400
    assert "new_password" in response.json()
    assert rows.get().metadata["reason"] == "invalid_new_password"


@pytest.mark.django_db
def test_missing_fields_return_400(client_for):
    response = client_for.post(URL, {"old_password": PASSWORD})

    assert response.status_code == 400
    assert "new_password" in response.json()


@pytest.mark.django_db
def test_unauthenticated_request_is_rejected(alice):
    response = APIClient().post(
        URL, {"old_password": PASSWORD, "new_password": UNIQUE_PASSWORD}
    )

    assert response.status_code == 401
    assert AuthAuditLog.objects.count() == 0


@pytest.mark.django_db
def test_password_validators_are_enabled(settings):
    assert settings.AUTH_PASSWORD_VALIDATORS, (
        "AUTH_PASSWORD_VALIDATORS is empty; "
        "test_weak_new_password_is_rejected would pass vacuously."
    )
