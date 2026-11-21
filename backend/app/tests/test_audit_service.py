import pytest
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from app.accounts.models import AuthAuditLog
from app.accounts.services import record_auth_event
from app.accounts.services.redaction import REDACTED


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.mark.django_db
def test_records_event_with_request_metadata(rf, settings):
    settings.AUDIT_TRUSTED_PROXY_COUNT = 0
    request = rf.post("/login/", REMOTE_ADDR="203.0.113.7", HTTP_USER_AGENT="pytest/1.0")
    log = record_auth_event(AuthAuditLog.EventType.LOGIN_FAILED, request=request, reason="bad_password")
    assert log.ip_address == "203.0.113.7"
    assert log.user_agent == "pytest/1.0"
    assert log.metadata == {"reason": "bad_password"}


@pytest.mark.django_db
def test_redacts_secrets_in_metadata(rf):
    request = rf.post("/login/", REMOTE_ADDR="203.0.113.7")
    log = record_auth_event(
        AuthAuditLog.EventType.LOGIN_FAILED,
        request=request,
        payload={"password": "hunter2", "nested": [{"refresh_token": "abc"}]},
    )
    assert log.metadata["payload"]["password"] == REDACTED
    assert log.metadata["payload"]["nested"][0]["refresh_token"] == REDACTED


@pytest.mark.django_db
def test_never_stores_model_instances(rf):
    user = get_user_model().objects.create_user(username="u1", password="x")
    request = rf.post("/login/", REMOTE_ADDR="203.0.113.7")
    log = record_auth_event(
        AuthAuditLog.EventType.LOGIN_SUCCESS, request=request, actor=user
    )
    assert isinstance(log.metadata["actor"], str)


@pytest.mark.django_db
def test_logging_failure_does_not_raise(monkeypatch, settings):
    settings.AUDIT_LOG_STRICT = False

    def boom(**kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(AuthAuditLog.objects, "create", boom)
    assert record_auth_event(AuthAuditLog.EventType.LOGIN_SUCCESS) is None


@pytest.mark.django_db
def test_strict_mode_raises(monkeypatch, settings):
    settings.AUDIT_LOG_STRICT = True

    def boom(**kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(AuthAuditLog.objects, "create", boom)
    with pytest.raises(RuntimeError):
        record_auth_event(AuthAuditLog.EventType.LOGIN_SUCCESS)


@pytest.mark.django_db
def test_oversized_metadata_is_truncated():
    log = record_auth_event(
        AuthAuditLog.EventType.LOGIN_FAILED, blob="x" * 50_000
    )
    assert log.metadata == {"truncated": True}
