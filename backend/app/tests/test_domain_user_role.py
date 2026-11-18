import pytest
from domain.entities import User, Role
from domain.validators import validate_password_strength
from domain.security_adapters import Argon2PasswordHasher

def test_role_creation():
    role = Role(id="role-1", name="Admin", permissions={"read", "write"})
    assert role.name == "Admin"
    assert "read" in role.permissions

def test_user_email_validation():
    user_valid = User(id="u-1", email="test@example.com")
    assert user_valid.validate_email() is True

    user_invalid = User(id="u-2", email="invalid-email")
    with pytest.raises(ValueError, match="Invalid email format"):
        user_invalid.validate_email()

def test_password_complexity_and_hashing():
    hasher = Argon2PasswordHasher()
    user = User(id="u-3", email="secure@example.com")
    
    # Weak password test
    with pytest.raises(ValueError):
        user.set_password("weak", hasher)

    # Strong password test
    user.set_password("Str0ng!P@ssword", hasher)
    assert user.password_hash is not None
    assert user.password_hash != "Str0ng!P@ssword"
    assert not hasattr(user, "password")

    # Verify password
    assert hasher.verify("Str0ng!P@ssword", user.password_hash) is True
    assert hasher.verify("WrongPassword1!", user.password_hash) is False
