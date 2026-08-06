"""Unit tests for Invoice model."""

from datetime import datetime
from pathlib import Path

from app.models.invoice import Invoice
from app.models.product import Product


def make_product():
    return Product(
        id="prod-1",
        description="Engine Part",
        part_number="PN-001",
        serial_number="SN-001",
        qty=2,
        unit="PCS",
        price=100.0,
        alternate="ALT-001",
        company="AirPart",
        document=None,
        image=None,
        timestamp=datetime(2026, 8, 1, 9, 0, 0),
    )


def test_invoice_initializes_with_provided_values():
    product = make_product()
    timestamp = datetime(2026, 8, 1, 10, 0, 0)
    due_date = datetime(2026, 8, 30, 10, 0, 0)
    invoice_doc = Path("/tmp/invoice.pdf")

    invoice = Invoice(
        invoice_id="inv-1",
        timestamp=timestamp,
        products=[product],
        customer="Customer A",
        seller="AirPart",
        bill_to="Customer Office",
        ship_to="Customer Warehouse",
        terms="Net 30",
        subtotal=200.0,
        descount=10.0,
        shipping=5.0,
        seles_tax=9.0,
        total=204.0,
        due_date=due_date,
        invoice_doc=invoice_doc,
    )

    assert invoice.invoice_id == "inv-1"
    assert invoice.timestamp == timestamp
    assert invoice.products == [product]
    assert invoice.customer == "Customer A"
    assert invoice.seller == "AirPart"
    assert invoice.bill_to == "Customer Office"
    assert invoice.ship_to == "Customer Warehouse"
    assert invoice.terms == "Net 30"
    assert invoice.subtotal == 200.0
    assert invoice.descount == 10.0
    assert invoice.shipping == 5.0
    assert invoice.seles_tax == 9.0
    assert invoice.total == 204.0
    assert invoice.due_date == due_date
    assert invoice.invoice_doc == invoice_doc


def test_invoice_generates_invoice_id_and_timestamp_when_not_provided(monkeypatch):
    fixed_timestamp = datetime(2026, 8, 1, 10, 0, 0)

    monkeypatch.setattr("app.models.invoice.idgen", lambda: "generated-invoice-id")
    monkeypatch.setattr("app.models.invoice.timestampgen", lambda: fixed_timestamp)

    invoice = Invoice(
        products=[],
        customer="Customer A",
        seller="AirPart",
        bill_to="Customer Office",
        ship_to="Customer Warehouse",
        terms="Net 30",
        subtotal=200.0,
        descount=10.0,
        shipping=5.0,
        seles_tax=9.0,
        total=204.0,
        due_date=datetime(2026, 8, 30, 10, 0, 0),
    )

    assert invoice.invoice_id == "generated-invoice-id"
    assert invoice.timestamp == fixed_timestamp


def test_invoice_to_dict_serializes_nested_products_and_adds_id():
    product = make_product()
    timestamp = datetime(2026, 8, 1, 10, 0, 0)
    due_date = datetime(2026, 8, 30, 10, 0, 0)
    invoice_doc = Path("/tmp/invoice.pdf")

    invoice = Invoice(
        invoice_id="inv-1",
        timestamp=timestamp,
        products=[product],
        customer="Customer A",
        seller="AirPart",
        bill_to="Customer Office",
        ship_to="Customer Warehouse",
        terms="Net 30",
        subtotal=200.0,
        descount=10.0,
        shipping=5.0,
        seles_tax=9.0,
        total=204.0,
        due_date=due_date,
        invoice_doc=invoice_doc,
    )

    result = invoice.to_dict()

    assert result["id"] == "inv-1"
    assert result["invoice_id"] == "inv-1"
    assert result["timestamp"] == "2026-08-01T10:00:00"
    assert result["due_date"] == "2026-08-30T10:00:00"
    assert result["invoice_doc"] == "/tmp/invoice.pdf"
    assert result["customer"] == "Customer A"
    assert result["products"] == [
        {
            "id": "prod-1",
            "timestamp": "2026-08-01T09:00:00",
            "description": "Engine Part",
            "part_number": "PN-001",
            "serial_number": "SN-001",
            "qty": 2,
            "unit": "PCS",
            "price": 100.0,
            "alternate": "ALT-001",
            "company": "AirPart",
            "document": None,
            "image": None,
        }
    ]


def test_invoice_from_dict_reconstructs_invoice_from_db_dict():
    data = {
        "id": "inv-1",
        "timestamp": "2026-08-01T10:00:00",
        "products": [
            {
                "id": "prod-1",
                "description": "Engine Part",
                "part_number": "PN-001",
                "serial_number": "SN-001",
                "qty": 2,
                "unit": "PCS",
                "price": 100.0,
                "alternate": "ALT-001",
                "company": "AirPart",
                "document": None,
                "image": None,
                "timestamp": None,
            }
        ],
        "customer": "Customer A",
        "seller": "AirPart",
        "bill_to": "Customer Office",
        "ship_to": "Customer Warehouse",
        "terms": "Net 30",
        "subtotal": 200.0,
        "descount": 10.0,
        "shipping": 5.0,
        "seles_tax": 9.0,
        "total": 204.0,
        "due_date": "2026-08-30T10:00:00",
        "invoice_doc": "/tmp/invoice.pdf",
    }

    invoice = Invoice.from_dict(data)

    assert isinstance(invoice, Invoice)
    assert invoice.invoice_id == "inv-1"
    assert invoice.timestamp == datetime(2026, 8, 1, 10, 0, 0)
    assert invoice.due_date == datetime(2026, 8, 30, 10, 0, 0)
    assert invoice.invoice_doc == Path("/tmp/invoice.pdf")
    assert invoice.customer == "Customer A"
    assert len(invoice.products) == 1
    assert isinstance(invoice.products[0], Product)
    assert invoice.products[0].id == "prod-1"
    assert invoice.products[0].description == "Engine Part"


def test_invoice_from_dict_uses_invoice_id_when_both_id_and_invoice_id_exist():
    data = {
        "id": "db-id",
        "invoice_id": "explicit-invoice-id",
        "timestamp": "2026-08-01T10:00:00",
        "products": [],
        "customer": "Customer A",
        "seller": "AirPart",
        "bill_to": "Customer Office",
        "ship_to": "Customer Warehouse",
        "terms": "Net 30",
        "subtotal": 200.0,
        "descount": 10.0,
        "shipping": 5.0,
        "seles_tax": 9.0,
        "total": 204.0,
        "due_date": "2026-08-30T10:00:00",
        "invoice_doc": None,
    }

    invoice = Invoice.from_dict(data)

    assert invoice.invoice_id == "explicit-invoice-id"


def test_invoice_from_dict_ignores_unknown_fields():
    data = {
        "id": "inv-1",
        "timestamp": "2026-08-01T10:00:00",
        "products": [],
        "customer": "Customer A",
        "seller": "AirPart",
        "bill_to": "Customer Office",
        "ship_to": "Customer Warehouse",
        "terms": "Net 30",
        "subtotal": 200.0,
        "descount": 10.0,
        "shipping": 5.0,
        "seles_tax": 9.0,
        "total": 204.0,
        "due_date": "2026-08-30T10:00:00",
        "invoice_doc": None,
        "unexpected_field": "should be ignored",
    }

    invoice = Invoice.from_dict(data)

    assert isinstance(invoice, Invoice)
    assert not hasattr(invoice, "unexpected_field")


def test_invoice_from_dict_handles_product_objects_without_reconstructing_them():
    product = make_product()

    data = {
        "id": "inv-1",
        "timestamp": "2026-08-01T10:00:00",
        "products": [product],
        "customer": "Customer A",
        "seller": "AirPart",
        "bill_to": "Customer Office",
        "ship_to": "Customer Warehouse",
        "terms": "Net 30",
        "subtotal": 200.0,
        "descount": 10.0,
        "shipping": 5.0,
        "seles_tax": 9.0,
        "total": 204.0,
        "due_date": "2026-08-30T10:00:00",
        "invoice_doc": None,
    }

    invoice = Invoice.from_dict(data)

    assert invoice.products == [product]
