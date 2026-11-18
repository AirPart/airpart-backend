from abc import ABC, abstractmethod

class PasswordHasher(ABC):
    """Port for password hashing so the domain stays framework-free."""

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        ...

    @abstractmethod
    def verify(self, plain_password: str, password_hash: str) -> bool:
        ...
