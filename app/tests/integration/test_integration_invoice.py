"""Integration tests for InvoiceRepository."""

import json
from pathlib import Path

from app.repository.invoice import InvoiceRepository


class TempJsonDB:
    """Small JSON-backed DB adapter for repository integration tests."""

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


def make_invoice(invoice_id="inv-1", customer="Customer A", total=100.0):
    return {
        "id": invoice_id,
        "invoice_id": invoice_id,
        "timestamp": "2026-08-01T10:00:00",
        "products": [
            {
                "id": "prod-1",
                "qty": 2,
            }
        ],
        "customer": customer,
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


def test_invoice_repository_adds_invoice_to_json_db(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1"))

    data = db.load()

    assert len(data["invoices"]) == 1
    assert data["invoices"][0]["id"] == "inv-1"
    assert data["invoices"][0]["customer"] == "Customer A"


def test_invoice_repository_get_all_returns_invoices(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1"))
    repo.add(make_invoice(invoice_id="inv-2"))

    invoices = repo.get_all()

    assert len(invoices) == 2
    assert invoices[0]["id"] == "inv-1"
    assert invoices[1]["id"] == "inv-2"


def test_invoice_repository_get_by_id_returns_matching_invoice(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1"))
    repo.add(make_invoice(invoice_id="inv-2"))

    invoice = repo.get_by_id("inv-2")

    assert invoice["id"] == "inv-2"


def test_invoice_repository_get_by_id_returns_none_for_missing_invoice(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1"))

    invoice = repo.get_by_id("missing-invoice")

    assert invoice is None


def test_invoice_repository_updates_existing_invoice(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1", customer="Old Customer", total=100.0))

    updated_invoice = make_invoice(
        invoice_id="inv-1",
        customer="Updated Customer",
        total=250.0,
    )

    repo.update("inv-1", updated_invoice)

    invoice = repo.get_by_id("inv-1")

    assert invoice["id"] == "inv-1"
    assert invoice["customer"] == "Updated Customer"
    assert invoice["total"] == 250.0


def test_invoice_repository_delete_removes_existing_invoice(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1"))
    repo.add(make_invoice(invoice_id="inv-2"))

    repo.delete("inv-1")

    invoices = repo.get_all()

    assert len(invoices) == 1
    assert invoices[0]["id"] == "inv-2"


def test_invoice_repository_delete_missing_invoice_keeps_data_unchanged(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = InvoiceRepository(db=db)

    repo.add(make_invoice(invoice_id="inv-1"))

    repo.delete("missing-invoice")

    invoices = repo.get_all()

    assert len(invoices) == 1
    assert invoices[0]["id"] == "inv-1"
