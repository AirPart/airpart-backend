import pytest
from django.test import RequestFactory

from app.accounts.services.audit import extract_client_info


@pytest.fixture
def rf():
    return RequestFactory()


def test_uses_remote_addr_by_default(rf, settings):
    settings.AUDIT_TRUSTED_PROXY_COUNT = 0
    request = rf.post("/login/", REMOTE_ADDR="203.0.113.7")
    assert extract_client_info(request)[0] == "203.0.113.7"


def test_ignores_forwarded_for_when_no_trusted_proxy(rf, settings):
    settings.AUDIT_TRUSTED_PROXY_COUNT = 0
    request = rf.post(
        "/login/",
        REMOTE_ADDR="203.0.113.7",
        HTTP_X_FORWARDED_FOR="1.2.3.4",
    )
    assert extract_client_info(request)[0] == "203.0.113.7"


def test_uses_forwarded_for_behind_one_trusted_proxy(rf, settings):
    settings.AUDIT_TRUSTED_PROXY_COUNT = 1
    request = rf.post(
        "/login/",
        REMOTE_ADDR="10.0.0.5",
        HTTP_X_FORWARDED_FOR="198.51.100.9, 10.0.0.5",
    )
    assert extract_client_info(request)[0] == "198.51.100.9"


def test_spoofed_forwarded_for_is_ignored(rf, settings):
    settings.AUDIT_TRUSTED_PROXY_COUNT = 1
    request = rf.post(
        "/login/",
        REMOTE_ADDR="10.0.0.5",
        HTTP_X_FORWARDED_FOR="1.1.1.1, 198.51.100.9, 10.0.0.5",
    )
    # attacker-supplied 1.1.1.1 is left of the trusted hop and must be dropped
    assert extract_client_info(request)[0] == "198.51.100.9"


def test_invalid_ip_becomes_none(rf, settings):
    settings.AUDIT_TRUSTED_PROXY_COUNT = 0
    request = rf.post("/login/", REMOTE_ADDR="not-an-ip")
    assert extract_client_info(request)[0] is None


def test_user_agent_is_truncated(rf):
    request = rf.post("/login/", HTTP_USER_AGENT="a" * 5000)
    assert len(extract_client_info(request)[1]) <= 512
