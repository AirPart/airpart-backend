"""Managing products"""

from datetime import datetime
from pathlib import Path

from utils import idgen, timestampgen


class Product:
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
