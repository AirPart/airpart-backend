"""Invoice Model"""

from datetime import datetime
from pathlib import Path

from app.models.product import Product
from app.services.deps import idgen, timestampgen

from .base import BaseModel


class Invoice(BaseModel):
    """Invoice model"""

    def __init__(
        self,
        products: list[Product],
        customer: str,
        seller: str,
        bill_to: str,
        ship_to: str,
        terms: str,  # due on receipt, Net 7, Net 15, Net 30, Net 60, Net 90
        subtotal: float,  # sum(quantity * unit_price)
        descount: float,
        shipping: float,
        seles_tax: float,
        total: float,  # subtotal + shipping + seles_tax - descount
        due_date: datetime,  # timestamp + terms
        invoice_doc: Path | None = None,
        id: str | None = None,
        invoice_id: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        self.id = (
            id
            if id is not None
            else (invoice_id if invoice_id is not None else str(idgen()))
        )
        self.timestamp = timestamp if timestamp is not None else timestampgen()
        self.products = products
        self.customer = customer
        self.seller = seller
        self.bill_to = bill_to
        self.ship_to = ship_to
        self.terms = terms
        self.subtotal = subtotal
        self.descount = descount
        self.shipping = shipping
        self.seles_tax = seles_tax
        self.total = total
        self.due_date = due_date
        self.invoice_doc = invoice_doc

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["invoice_id"] = self.id
        return data

    @property
    def invoice_id(self) -> str:
        return self.id

    @invoice_id.setter
    def invoice_id(self, value: str) -> None:
        self.id = value

    @classmethod
    def from_dict(cls, data: dict) -> "Invoice":
        """Reconstruct Invoice model instance from a dictionary"""
        data_copy = dict(data)

        if "invoice_id" in data_copy:
            data_copy["id"] = data_copy.pop("invoice_id")

        # backward compatibility: invoice_id -> id
        if "id" not in data_copy and "invoice_id" in data_copy:
            data_copy["id"] = data_copy.pop("invoice_id")
        # cononical id
        if "invoice_id" in data_copy:
            data_copy.pop("invoice_id")

        # products
        raw_product = data_copy.get("products") or []
        if not isinstance(raw_product, list):
            raise TypeError("product must be a list")

        products: list[Product] = []
        for p in raw_product:
            if isinstance(p, Product):
                products.append(p)
            elif isinstance(p, dict):
                products.append(Product.from_dict(p))
            else:
                raise TypeError(f"Invalid product item type: {type(p)!r}")

        data_copy["products"] = products

        # datetimes
        raw_product = data_copy.get("products") or []
        for field in ("due_date", "timestamp"):
            v = data_copy.get(field)
            if isinstance(v, str):
                data_copy[field] = datetime.fromisoformat(v)

        # invoice_doc
        doc = data_copy.get("invoice_doc")
        if isinstance(doc, str) and doc != "":
            data_copy["invoice_doc"] = Path(doc)

        init_params = {
            "products",
            "customer",
            "seller",
            "bill_to",
            "ship_to",
            "terms",
            "subtotal",
            "descount",
            "shipping",
            "seles_tax",
            "total",
            "due_date",
            "invoice_doc",
            "id",
            "timestamp",
        }

        filtered = {k: v for k, v in data_copy.items() if k in init_params}

        return cls(**filtered)
