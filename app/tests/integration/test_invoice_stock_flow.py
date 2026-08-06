"""Integration tests for invoice/product stock workflows."""

import json
from datetime import datetime
from pathlib import Path

from app.models.product import Product
from app.repository.invoice import InvoiceRepository
from app.repository.product import ProductRepository
from app.services.invoice import InvoiceService
from app.services.products.product import ProductService


class TempJsonDB:
    """Small JSON-backed DB adapter for integration flow tests."""

    def __init__(self, path):
        self.path = Path(path)
        self.path.write_text(
            json.dumps({"products": [], "invoices": []}),
            encoding="utf-8",
        )

    def load(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data):
        self.path.write_text(json.dumps(data), encoding="utf-8")


def make_product(product_id="prod-1", qty=10):
    return Product(
        id=product_id,
        description="Engine Part",
        part_number="PN-001",
        serial_number="SN-001",
        qty=qty,
        unit="PCS",
        price=100.0,
        alternate="ALT-001",
        company="AirPart",
        document=None,
        image=None,
        timestamp=datetime(2026, 8, 1, 10, 0, 0),
    )


def make_invoice(invoice_id="inv-1", product_id="prod-1", qty=2, total=200.0):
    return {
        "id": invoice_id,
        "invoice_id": invoice_id,
        "timestamp": "2026-08-01T10:00:00",
        "products": [
            {
                "id": product_id,
                "qty": qty,
            }
        ],
        "customer": "Customer A",
        "seller": "AirPart",
        "bill_to": "Customer Office",
        "ship_to": "Customer Warehouse",
        "terms": "Net 30",
        "subtotal": total,
        "descount": 0.0,
        "shipping": 0.0,
        "seles_tax": 0.0,
        "total": total,
        "due_date": "2026-08-30T10:00:00",
        "invoice_doc": None,
    }


def make_services(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")

    product_repo = ProductRepository(db=db)
    invoice_repo = InvoiceRepository(db=db)

    product_service = ProductService(db=db, repo=product_repo)
    invoice_service = InvoiceService(repo=invoice_repo)

    return db, product_service, invoice_service


def test_invoice_creation_flow_decreases_product_stock_and_saves_invoice(tmp_path):
    db, product_service, invoice_service = make_services(tmp_path)

    product_service.addproduct(make_product(product_id="prod-1", qty=10))

    selected_product = product_service.get_a_product_by_id("prod-1")
    requested_qty = 3

    assert selected_product["qty"] == 10

    product_service.decrease_qty("prod-1", requested_qty)
    invoice_service.add_invoice(
        make_invoice(
            invoice_id="inv-1",
            product_id="prod-1",
            qty=requested_qty,
            total=300.0,
        )
    )

    updated_product = product_service.get_a_product_by_id("prod-1")
    saved_invoice = invoice_service.get_a_invoice_by_id("inv-1")

    assert updated_product["qty"] == 7
    assert saved_invoice["id"] == "inv-1"
    assert saved_invoice["products"] == [{"id": "prod-1", "qty": 3}]

    data = db.load()
    assert len(data["products"]) == 1
    assert len(data["invoices"]) == 1


def test_invoice_edit_flow_restores_old_stock_and_applies_new_stock(tmp_path):
    _, product_service, invoice_service = make_services(tmp_path)

    product_service.addproduct(make_product(product_id="prod-1", qty=10))

    product_service.decrease_qty("prod-1", 2)
    invoice_service.add_invoice(make_invoice(invoice_id="inv-1", qty=2, total=200.0))

    product_after_first_invoice = product_service.get_a_product_by_id("prod-1")
    assert product_after_first_invoice["qty"] == 8

    old_invoice = invoice_service.get_a_invoice_by_id("inv-1")
    old_product = old_invoice["products"][0]

    product_service.increase_qty(old_product["id"], old_product["qty"])

    product_after_restore = product_service.get_a_product_by_id("prod-1")
    assert product_after_restore["qty"] == 10

    new_invoice = make_invoice(invoice_id="inv-1", qty=5, total=500.0)
    new_product = new_invoice["products"][0]

    product_service.decrease_qty(new_product["id"], new_product["qty"])
    invoice_service.edit_invoice("inv-1", new_invoice)

    final_product = product_service.get_a_product_by_id("prod-1")
    final_invoice = invoice_service.get_a_invoice_by_id("inv-1")

    assert final_product["qty"] == 5
    assert final_invoice["products"] == [{"id": "prod-1", "qty": 5}]
    assert final_invoice["total"] == 500.0


def test_invoice_creation_flow_does_not_decrease_stock_when_qty_is_insufficient(
    tmp_path,
):
    _, product_service, invoice_service = make_services(tmp_path)

    product_service.addproduct(make_product(product_id="prod-1", qty=1))

    product = product_service.get_a_product_by_id("prod-1")
    requested_qty = 5

    assert product["qty"] < requested_qty

    if product["qty"] >= requested_qty:
        product_service.decrease_qty("prod-1", requested_qty)
        invoice_service.add_invoice(make_invoice(qty=requested_qty))

    unchanged_product = product_service.get_a_product_by_id("prod-1")
    invoices = invoice_service.get_all_invoice()

    assert unchanged_product["qty"] == 1
    assert invoices == []
