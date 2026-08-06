"""Integration tests for ProductRepository."""

import json
from datetime import datetime
from pathlib import Path

from app.models.product import Product
from app.repository.product import ProductRepository


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


def make_product(
    product_id="prod-1",
    qty=10,
    document=None,
    image=None,
):
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
        document=document,
        image=image,
        timestamp=datetime(2026, 8, 1, 10, 0, 0),
    )


def test_product_repository_adds_product_to_json_db(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    product = make_product(product_id="prod-1")

    repo.add(product)

    data = db.load()

    assert len(data["products"]) == 1
    assert data["products"][0]["id"] == "prod-1"
    assert data["products"][0]["description"] == "Engine Part"


def test_product_repository_get_all_returns_products(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    repo.add(make_product(product_id="prod-1"))
    repo.add(make_product(product_id="prod-2"))

    products = repo.get_all()

    assert len(products) == 2
    assert products[0]["id"] == "prod-1"
    assert products[1]["id"] == "prod-2"


def test_product_repository_get_by_id_returns_matching_product(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    repo.add(make_product(product_id="prod-1"))
    repo.add(make_product(product_id="prod-2"))

    product = repo.get_by_id("prod-2")

    assert product["id"] == "prod-2"


def test_product_repository_get_by_id_returns_none_for_missing_product(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    repo.add(make_product(product_id="prod-1"))

    product = repo.get_by_id("missing-product")

    assert product is None


def test_product_repository_updates_existing_product(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    repo.add(make_product(product_id="prod-1", qty=10))

    updated_product = make_product(product_id="prod-1", qty=25)
    updated_product.description = "Updated Engine Part"

    repo.update("prod-1", updated_product)

    product = repo.get_by_id("prod-1")

    assert product["id"] == "prod-1"
    assert product["qty"] == 25
    assert product["description"] == "Updated Engine Part"


def test_product_repository_delete_removes_existing_product(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    repo.add(make_product(product_id="prod-1"))
    repo.add(make_product(product_id="prod-2"))

    repo.delete("prod-1")

    products = repo.get_all()

    assert len(products) == 1
    assert products[0]["id"] == "prod-2"


def test_product_repository_delete_missing_product_keeps_data_unchanged(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    repo.add(make_product(product_id="prod-1"))

    repo.delete("missing-product")

    products = repo.get_all()

    assert len(products) == 1
    assert products[0]["id"] == "prod-1"


def test_product_repository_delete_removes_product_files(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    repo = ProductRepository(db=db)

    document = tmp_path / "manual.pdf"
    image = tmp_path / "image.png"

    document.write_text("document content", encoding="utf-8")
    image.write_text("image content", encoding="utf-8")

    repo.add(
        make_product(
            product_id="prod-1",
            document=document,
            image=image,
        )
    )

    assert document.exists()
    assert image.exists()

    repo.delete("prod-1")

    assert repo.get_by_id("prod-1") is None
    assert not document.exists()
    assert not image.exists()
