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
        invoice_id: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        self.invoice_id = invoice_id if invoice_id is not None else str(idgen())
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
        """Return dict from model compatible with DB layout"""
        data = super().to_dict()
        data["id"] = self.invoice_id
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Invoice":
        """Reconstruct Invoice model instance from a dictionary"""
        data_copy = data.copy()

        product_raw = data_copy.get("products") or []
        products = []
        for p in product_raw:
            if isinstance(p, dict):
                try:
                    if hasattr(Product, "from_dict"):
                        products.append(Product.from_dict(p))
                    else:
                        products.append(Product(**p))

                except TypeError:
                    products.append(p)
            else:
                products.append(p)
        data_copy["products"] = products

        for data_field in ["due_date", "timestamp"]:
            val = data_copy.get(data_field)
            if isinstance(val, str):
                try:
                    data_copy[data_field] = datetime.fromisoformat(val)
                except ValueError:
                    data_copy[data_field] = datetime.utcnow()

        doc_path = data_copy.get("invoice_doc")
        if doc_path and isinstance(doc_path, str):
            data_copy["invoice_doc"] = Path(doc_path)

        if "id" in data_copy and "invoice_id" not in data_copy:
            data_copy["invoice_id"] = data_copy.pop("id")
        elif "id" in data_copy:
            data_copy.pop("id")

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
            "invoice_id",
            "timestamp",
        }

        filtered_data = {k: v for k, v in data_copy.items() if k in init_params}

        return cls(**filtered_data)
