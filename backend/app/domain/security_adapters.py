from argon2 import PasswordHasher as Argon2Hasher
from .security import PasswordHasher

class Argon2PasswordHasher(PasswordHasher):
    def __init__(self):
        self._hasher = Argon2Hasher()

    def hash(self, plain_password: str) -> str:
        return self._hasher.hash(plain_password)

    def verify(self, plain_password: str, password_hash: str) -> bool:
        try:
            return self._hasher.verify(password_hash, plain_password)
        except Exception:
            return False
