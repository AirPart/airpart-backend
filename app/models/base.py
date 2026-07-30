"""Base model"""

from datetime import datetime
from pathlib import Path


class BaseModel:
    """Base model with reusable serialization logic"""

    def _serialize_value(self, value):
        """Convert model values to JSON-serializable values"""
        if isinstance(value, BaseModel):
            return value.to_dict()

        if isinstance(value, list):
            return [self._serialize_value(item) for item in value]

        if isinstance(value, tuple):
            return [self._serialize_value(item) for item in value]

        if isinstance(value, dict):
            return {key: self._serialize_value(val) for key, val in value.items()}

        if isinstance(value, datetime):
            return value.isoformat()

        if isinstance(value, Path):
            return str(value)

        return value

    def to_dict(self) -> dict:
        """Return dict from model"""
        return {
            key: self._serialize_value(value)
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Generic constructor from dict - can be overridden in child models"""
        return cls(**data)
