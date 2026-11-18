from dataclasses import dataclass, field
from typing import Set, Optional
import re

from .validators import validate_password_strength
from .security import PasswordHasher

@dataclass
class Role:
    id: str
    name: str
    permissions: Set[str] = field(default_factory=set)

@dataclass
class User:
    id: str
    email: str
    password_hash: Optional[str] = None
    roles: Set[Role] = field(default_factory=set)
    is_active: bool = True

    def validate_email(self) -> bool:
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, self.email):
            raise ValueError("Invalid email format.")
        return True
    
    def set_password(self, plain_password: str, hasher: PasswordHasher) -> None:
        validate_password_strength(plain_password)
        self.password_hash = hasher.hash(plain_password)

