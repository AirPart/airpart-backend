"""Validation, workflow and Bussines logic invoice"""

from typing import List

from app.models.invoice import Invoice
from app.repository.invoice import InvoiceRepository


class InvoiceService:
    """Bussines logic, validation and wrokfolw invoice service"""

    def __init__(self, repo: InvoiceRepository) -> None:
        self.repo = repo

    def get_all_invoice(self) -> List[Invoice]:
        """Get all invoice workflow, validation and Bussines logic"""
        return self.repo.get_all()

    def get_a_invoice_by_id(self, invoice_id) -> Invoice | None:
        """Get a invoice workflow, validation and Bussines logic"""
        return self.repo.get_by_id(invoice_id=invoice_id)

    def add_invoice(self, invoice: Invoice) -> None:
        """Add a invoice workflow, validation and Bussines logic"""
        self.repo.add(invoice)

    def delete_a_invoice(self, invoice_id: str) -> None:
        """Remove invoice workflow, validation and Bussines logic"""
        self.repo.delete(invoice_id=invoice_id)

    def edit_invoice(self, invoice_id: str, new_invoice: Invoice):
        """Edit invoice workflow, validation and Bussines logic"""
        self.repo.update(invoice_id=invoice_id, new_invoice=new_invoice)
