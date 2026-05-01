"""Managing products"""

from datetime import datetime
from pathlib import Path

from utils import idgen, timestampgen


class Product:
    """Product object for create a product"""

    def __init__(
        self,
        discription: str,
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
        self.discription = discription
        self.part_number = part_number
        self.serial_number = serial_number
        self.qty = qty
        self.unit = unit
        self.price = price
        self.alternate = alternate
        self.company = company
        self.document = document
        self.image = image

    def to_dict(self) -> dict:
        """Return dict from product object"""
        return {
            "discription": self.discription,
            "part_number": self.part_number,
            "serial_number": self.serial_number,
            "qty": self.qty,
            "unit": self.unit,
            "price": self.price,
            "alternate": self.alternate,
            "company": self.company,
            "id": self.id,
            "document": self.document,
            "image": self.image,
            "timestamp": self.timestamp,
        }
