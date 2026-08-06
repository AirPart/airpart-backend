"""Unit tests for Product model."""

from datetime import datetime
from pathlib import Path

from app.models.product import Product


def test_product_initializes_with_provided_values():
    timestamp = datetime(2026, 8, 1, 10, 30, 0)
    document = Path("/tmp/manual.pdf")
    image = Path("/tmp/image.png")

    product = Product(
        id="prod-1",
        description="Engine Part",
        part_number="PN-001",
        serial_number="SN-001",
        qty=10,
        unit="PCS",
        price=120.5,
        alternate="ALT-001",
        company="AirPart",
        document=document,
        image=image,
        timestamp=timestamp,
    )

    assert product.id == "prod-1"
    assert product.description == "Engine Part"
    assert product.part_number == "PN-001"
    assert product.serial_number == "SN-001"
    assert product.qty == 10
    assert product.unit == "PCS"
    assert product.price == 120.5
    assert product.alternate == "ALT-001"
    assert product.company == "AirPart"
    assert product.document == document
    assert product.image == image
    assert product.timestamp == timestamp


def test_product_generates_id_and_timestamp_when_not_provided(monkeypatch):
    fixed_timestamp = datetime(2026, 8, 1, 12, 0, 0)

    monkeypatch.setattr("app.models.product.idgen", lambda: "generated-product-id")
    monkeypatch.setattr("app.models.product.timestampgen", lambda: fixed_timestamp)

    product = Product(
        description="Engine Part",
        part_number="PN-001",
        serial_number="SN-001",
        qty=10,
        unit="PCS",
        price=120.5,
        alternate="ALT-001",
        company="AirPart",
    )

    assert product.id == "generated-product-id"
    assert product.timestamp == fixed_timestamp


def test_product_to_dict_serializes_datetime_and_paths():
    timestamp = datetime(2026, 8, 1, 10, 30, 0)
    document = Path("/tmp/manual.pdf")
    image = Path("/tmp/image.png")

    product = Product(
        id="prod-1",
        description="Engine Part",
        part_number="PN-001",
        serial_number="SN-001",
        qty=10,
        unit="PCS",
        price=120.5,
        alternate="ALT-001",
        company="AirPart",
        document=document,
        image=image,
        timestamp=timestamp,
    )

    result = product.to_dict()

    assert result == {
        "id": "prod-1",
        "timestamp": "2026-08-01T10:30:00",
        "description": "Engine Part",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 120.5,
        "alternate": "ALT-001",
        "company": "AirPart",
        "document": "/tmp/manual.pdf",
        "image": "/tmp/image.png",
    }


def test_product_to_dict_handles_optional_document_and_image_as_none():
    timestamp = datetime(2026, 8, 1, 10, 30, 0)

    product = Product(
        id="prod-1",
        description="Engine Part",
        part_number="PN-001",
        serial_number="SN-001",
        qty=10,
        unit="PCS",
        price=120.5,
        alternate="ALT-001",
        company="AirPart",
        document=None,
        image=None,
        timestamp=timestamp,
    )

    result = product.to_dict()

    assert result["document"] is None
    assert result["image"] is None


def test_product_from_dict_creates_product_instance():
    data = {
        "id": "prod-1",
        "description": "Engine Part",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 120.5,
        "alternate": "ALT-001",
        "company": "AirPart",
        "document": None,
        "image": None,
        "timestamp": None,
    }

    product = Product.from_dict(data)

    assert isinstance(product, Product)
    assert product.id == "prod-1"
    assert product.description == "Engine Part"
    assert product.part_number == "PN-001"
    assert product.serial_number == "SN-001"
    assert product.qty == 10
    assert product.unit == "PCS"
    assert product.price == 120.5
    assert product.alternate == "ALT-001"
    assert product.company == "AirPart"
    assert product.document is None
    assert product.image is None
    assert product.timestamp is not None
