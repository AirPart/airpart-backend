import pytest

from app.accounts.services.redaction import REDACTED, redact


@pytest.mark.parametrize(
    "key",
    [
        "password", "new_password", "old_password", "token", "access",
        "refresh", "access_token", "refresh_token", "authorization",
        "password_hash", "PASSWORD", "AccessToken", "client_secret",
        "refresh-token", "apiToken",
    ],
)
def test_sensitive_keys_are_redacted(key):
    assert redact({key: "super-secret"}) == {key: REDACTED}


@pytest.mark.parametrize("key", ["username", "event", "reason", "ip", "role"])
def test_safe_keys_are_kept(key):
    assert redact({key: "value"}) == {key: "value"}


def test_nested_dicts_are_redacted():
    payload = {"outer": {"inner": {"password": "x", "safe": 1}}}
    assert redact(payload) == {"outer": {"inner": {"password": REDACTED, "safe": 1}}}


def test_lists_of_dicts_are_redacted():
    payload = {"attempts": [{"token": "a"}, {"token": "b"}]}
    assert redact(payload) == {"attempts": [{"token": REDACTED}, {"token": REDACTED}]}


def test_deeply_mixed_structures():
    payload = {"a": [{"b": [{"refresh_token": "t", "keep": [1, 2]}]}]}
    result = redact(payload)
    assert result["a"][0]["b"][0]["refresh_token"] == REDACTED
    assert result["a"][0]["b"][0]["keep"] == [1, 2]


def test_does_not_mutate_input():
    payload = {"password": "x"}
    redact(payload)
    assert payload == {"password": "x"}


def test_handles_non_string_keys_and_values():
    assert redact({1: "one", "token": None}) == {1: "one", "token": REDACTED}
