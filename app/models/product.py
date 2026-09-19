"""Managing products"""

from datetime import datetime
from pathlib import Path

from app.services.deps import idgen, timestampgen

from .base import BaseModel


class Product(BaseModel):
    """Product object for create a product"""

    def __init__(
        self,
        description: str,
        part_number: str,
        serial_number: str,
        qty: int,
        unit: str,
        price: float,
        alternate: str,
        company: str,
        id: str | None = None,
        document: Path | None = None,
        image: Path | None = None,
        timestamp: datetime | None = None,
    ) -> None:

        self.id = id if id is not None else str(idgen())
        self.timestamp = timestamp if timestamp is not None else timestampgen()
        self.description = description
        self.part_number = part_number
        self.serial_number = serial_number
        self.qty = qty
        self.unit = unit
        self.price = price
        self.alternate = alternate
        self.company = company
        self.document = document
        self.image = image

    @classmethod
    def from_dict(cls, data: dict) -> "Product":
        data_copy = dict(data)

        # timestamp: str -> datetime
        ts = data_copy.get("timestamp")
        if isinstance(ts, str):
            data_copy["timestamp"] = datetime.fromisoformat(ts)

        # document/image: str -> Path
        for field in ("document", "image"):
            v = data_copy.get(field)
            if isinstance(v, str) and v != "":
                data_copy[field] = Path(v)

        init_params = {
            "description",
            "part_number",
            "serial_number",
            "qty",
            "unit",
            "price",
            "alternate",
            "company",
            "id",
            "document",
            "image",
            "timestamp",
        }

        filtered = {k: v for k, v in data_copy.items() if k in init_params}

        return cls(**filtered)
