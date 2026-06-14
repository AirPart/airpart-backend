"""Invoice Model"""

from datetime import datetime
from pathlib import Path

from app.services.deps import idgen, timestampgen
from app.services.products.model import Product


class Invoice:
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
        """Return dict from invoice model"""
        return {
            "products": self.products,
            "customer": self.customer,
            "seller": self.seller,
            "bill_to": self.bill_to,
            "ship_to": self.ship_to,
            "terms": self.terms,
            "subtotal": self.subtotal,
            "descount": self.descount,
            "shipping": self.shipping,
            "seles_tax": self.seles_tax,
            "total": self.total,
            "due_date": self.due_date,
            "invoice_id": self.invoice_id,
            "timestamp": self.timestamp,
            "invoice_doc": self.invoice_doc,
        }
