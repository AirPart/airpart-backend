"""Integration-style tests for InvoiceRepository."""

from app.core.db import JsonDB
from app.repository.invoice import InvoiceRepository


def make_invoice_repo(tmp_path, initial_data=None):
    """Create InvoiceRepository with isolated temporary JsonDB."""
    db_file = tmp_path / "db.json"
    db = JsonDB(str(db_file))

    if initial_data is not None:
        db.save(initial_data)

    repo = InvoiceRepository(db=db)
    return repo, db


def test_get_all_invoices_returns_empty_list_when_db_file_missing(tmp_path):
    repo, _ = make_invoice_repo(tmp_path)

    result = repo.get_all()

    assert result == []


def test_get_all_invoices_returns_saved_invoices(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Ali"},
            {"id": "inv-2", "customer": "Reza"},
        ],
    }
    repo, _ = make_invoice_repo(tmp_path, initial_data)

    result = repo.get_all()

    assert result == initial_data["invoices"]


def test_get_by_id_returns_invoice_when_invoice_exists(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Ali"},
            {"id": "inv-2", "customer": "Reza"},
        ],
    }
    repo, _ = make_invoice_repo(tmp_path, initial_data)

    result = repo.get_by_id("inv-2")

    assert result == {"id": "inv-2", "customer": "Reza"}


def test_get_by_id_returns_none_when_invoice_does_not_exist(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Ali"},
        ],
    }
    repo, _ = make_invoice_repo(tmp_path, initial_data)

    result = repo.get_by_id("missing-invoice")

    assert result is None


def test_add_invoice_persists_invoice_to_json_db(tmp_path):
    repo, db = make_invoice_repo(
        tmp_path,
        {
            "products": [],
            "invoices": [],
        },
    )

    invoice = {
        "id": "inv-1",
        "invoice_id": "inv-1",
        "customer": "Ali",
        "products": [],
        "total": 100.0,
    }

    result = repo.add(invoice)

    assert result is None

    saved_data = db.load()
    assert saved_data["invoices"] == [invoice]


def test_delete_invoice_removes_invoice_from_json_db(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Ali"},
            {"id": "inv-2", "customer": "Reza"},
        ],
    }
    repo, db = make_invoice_repo(tmp_path, initial_data)

    result = repo.delete("inv-1")

    assert result is None

    saved_data = db.load()
    assert saved_data["invoices"] == [
        {"id": "inv-2", "customer": "Reza"},
    ]


def test_delete_invoice_keeps_data_unchanged_when_invoice_not_found(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Ali"},
        ],
    }
    repo, db = make_invoice_repo(tmp_path, initial_data)

    result = repo.delete("missing-invoice")

    assert result is None

    saved_data = db.load()
    assert saved_data["invoices"] == initial_data["invoices"]


def test_update_invoice_replaces_existing_invoice(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Old Customer", "total": 100.0},
            {"id": "inv-2", "customer": "Another Customer", "total": 200.0},
        ],
    }
    repo, db = make_invoice_repo(tmp_path, initial_data)

    new_invoice = {
        "id": "inv-1",
        "customer": "Updated Customer",
        "total": 150.0,
    }

    result = repo.update("inv-1", new_invoice)

    assert result is None

    saved_data = db.load()
    assert saved_data["invoices"] == [
        new_invoice,
        {"id": "inv-2", "customer": "Another Customer", "total": 200.0},
    ]


def test_update_invoice_keeps_data_unchanged_when_invoice_not_found(tmp_path):
    initial_data = {
        "products": [],
        "invoices": [
            {"id": "inv-1", "customer": "Ali"},
        ],
    }
    repo, db = make_invoice_repo(tmp_path, initial_data)

    new_invoice = {
        "id": "missing-invoice",
        "customer": "Updated Customer",
    }

    result = repo.update("missing-invoice", new_invoice)

    assert result is None

    saved_data = db.load()
    assert saved_data["invoices"] == initial_data["invoices"]
