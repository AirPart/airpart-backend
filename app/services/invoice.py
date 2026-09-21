"""Validation, workflow and Bussines logic invoice"""

from datetime import datetime
from typing import Any, Dict, List

from app.core.extenction import (
    InsufficientStockError,
    InvoiceNotFoundError,
    ProductNotFoundError,
    ValidationError,
)
from app.models.invoice import Invoice
from app.repository.invoice import InvoiceRepository
from app.services.products.product import ProductService


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
        invoice = self.get_a_invoice_by_id(invoice_id)
        if not invoice:
            raise InvoiceNotFoundError(invoice_id)
        self.repo.delete(invoice_id=invoice_id)

    def edit_invoice(self, invoice_id: str, new_invoice: Invoice | dict) -> None:
        """Edit invoice workflow, validation and Bussines logic"""
        self.repo.update(invoice_id=invoice_id, new_invoice=new_invoice)

    # ----------------------------------------------------------------
    # Core Domain Logic (Stock adjustment & Invoice Orchestration)
    # ----------------------------------------------------------------

    @staticmethod
    def _extract_product_id_and_qty(item: Any) -> tuple[str, int]:
        """Extract id and qty safely from dict or object"""
        if isinstance(item, dict):
            prod_id = item.get("id") or item.get("product_id")
            qty = int(item.get("qty", 0))
        else:
            prod_id = getattr(item, "id", None) or getattr(item, "product_id", None)
            qty = int(getattr(item, "qty", 0))

        if not prod_id:
            raise ValidationError("Product item missing 'id' or 'product_id'.")
        return str(prod_id), qty

    def create_invoice_with_stock(
        self,
        invoice_data: Dict[str, Any],
        product_service: ProductService,
    ) -> Invoice:
        """Validate stock, deduct inventory, and persist new invoice.
        All-or-nothing validation prevents corupted stock states."""
        raw_products = invoice_data.get("products")
        if not raw_products or not isinstance(raw_products, list):
            raise ValidationError("No products provided or invalid format.")

        # 1. Step 1: Pre-validate all items before making any state mutations
        item_to_process: list[tuple[str, int]] = []
        for item in raw_products:
            prod_id, req_qty = self._extract_product_id_and_qty(item)
            db_product = product_service.get_a_product_by_id(prod_id)

            if not db_product:
                raise ProductNotFoundError(prod_id)

            curr_qty = (
                db_product.get("qty", 0)
                if isinstance(db_product, dict)
                else getattr(db_product, "qty", 0)
            )

            if curr_qty < req_qty:
                raise InsufficientStockError(
                    product_id=prod_id,
                    available_qty=curr_qty,
                    requested_qty=req_qty,
                )

            item_to_process.append((prod_id, req_qty))

        # 2. Step 2: Safe deduction from inventory
        for prod_id, req_qty in item_to_process:
            product_service.decrease_qty(prod_id, req_qty)

        # 3. Step 3: Construct Invoice Model
        try:
            due_date_raw = invoice_data.get("due_date")
            timestamp_raw = invoice_data.get("timestamp")

            invoice = Invoice(
                products=raw_products,
                customer=invoice_data.get("customer", ""),
                seller=invoice_data.get("seller", ""),
                bill_to=invoice_data.get("bill_to", ""),
                ship_to=invoice_data.get("ship_to", ""),
                terms=invoice_data.get("terms", "Net 30"),
                subtotal=float(invoice_data.get("subtotal", 0.0)),
                descount=float(invoice_data.get("descount", 0.0)),
                shipping=float(invoice_data.get("shipping", 0.0)),
                seles_tax=float(invoice_data.get("seles_tax", 0.0)),
                total=float(invoice_data.get("total", 0.0)),
                due_date=(
                    datetime.fromisoformat(due_date_raw)
                    if due_date_raw
                    else datetime.utcnow()
                ),
                invoice_id=invoice_data.get("invoice_id") or invoice_data.get("id"),
                timestamp=(
                    datetime.fromisoformat(timestamp_raw) if timestamp_raw else None
                ),
            )

            self.add_invoice(invoice.to_dict())
            return invoice
        except Exception:
            # Rollback inventory deduction if invoice creation fails
            for prod_id, req_qty in item_to_process:
                product_service.increase_qty(prod_id, req_qty)
            raise

    def update_invoice_with_stock(
        self,
        invoice_id: str,
        new_invoice_data: Dict[str, Any],
        product_service: ProductService,
    ) -> Invoice:
        """Revert old invoice stock, validate new items, and update invoice."""
        old_invoice_data = self.get_a_invoice_by_id(invoice_id)
        if not old_invoice_data:
            raise InvoiceNotFoundError(invoice_id)

        if not new_invoice_data or not isinstance(new_invoice_data, dict):
            raise ValidationError("Missing 'new_invoice' data")

        new_invoice = (
            Invoice.from_dict(new_invoice_data)
            if not isinstance(new_invoice_data, Invoice)
            else new_invoice_data
        )

        # 1. Step 1: Temporary revert old stock
        old_items: list[tuple[str, int]] = []
        for prod in new_invoice.products:
            prod_id, qty = self._extract_product_id_and_qty(prod)
            product_service.increase_qty(prod_id, qty)
            old_items.append((prod_id, qty))

        # 2. Step 2: Validate new stock
        new_items: list[tuple[str, int]] = []
        try:
            for prod in new_invoice.products:
                prod_id, req_qty = self._extract_product_id_and_qty(prod)
                db_product = product_service.get_a_invoice_by_id(prod_id)

                if not db_product:
                    raise ProductNotFoundError(prod_id)

                curr_qty = (
                    db_product.get("qty", 0)
                    if isinstance(db_product, dict)
                    else getattr(db_product, "qty", 0)
                )
                if curr_qty < req_qty:
                    raise InsufficientStockError(
                        product_id=prod_id,
                        available_qty=curr_qty,
                        requested_qty=req_qty,
                    )
                new_items.append((prod_id, req_qty))

            # 3. Step 3: Deduct new stock
            for prod_id, req_qty in new_items:
                product_service.decrease_qty(prod_id, req_qty)

            self.edit_invoice(invoice_id, new_invoice.to_dict())
            return new_invoice
        except:
            # Rollback undo old items increase to leave DB exactly as it was
            for prod_id, qty in old_items:
                product_service.decrease_qty(prod_id, qty)
            raise
