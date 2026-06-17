"""Data access, relation database and all intraction with database"""

from typing import List

from app.core.db import JsonDB
from app.models.invoice import Invoice


class InvoiceRepository:
    """Invoice data access repository"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def get_all(self) -> List[Invoice]:
        """Return all invoice from json file"""
        data = self.db.load()
        return data["invoices"]

    def get_by_id(self, invoice_id: str) -> Invoice | None:
        """Return a invoice from json file with invoice ID"""
        data = self.db.load()
        for invoice in data["invoices"]:
            if invoice["id"] == invoice_id:
                return invoice
        return None

    def add(self, invoice: Invoice) -> None:
        """Add invoice in json file with invoice object"""
        data = self.db.load()

        data["invoices"].append(invoice)

        self.db.save(data)

    def delete(self, invoice_id: str) -> None:
        """Remove invoice from json file with invoice ID"""
        data = self.db.load()
        for invoice in data["invoices"]:
            if invoice["id"] == invoice_id:
                data["invoices"].remove(invoice)

        self.db.save(data)

    def update(self, invoice_id: str, new_invoice: Invoice) -> None:
        """Edit invoice in json file with invoice ID and new invoice object"""
        data = self.db.load()
        for index, invoice in enumerate(data["invoices"]):
            if invoice["id"] == invoice_id:
                data["invoices"][index] = new_invoice
        self.db.save(data)
