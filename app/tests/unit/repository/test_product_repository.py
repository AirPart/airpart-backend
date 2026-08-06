"""Integration-style tests for ProductRepository."""

from unittest.mock import MagicMock

from app.core.db import JsonDB
from app.repository.product import ProductRepository


def make_product_repo(tmp_path, initial_data=None):
    """Create ProductRepository with isolated temporary JsonDB."""
    db_file = tmp_path / "db.json"
    db = JsonDB(str(db_file))

    if initial_data is not None:
        db.save(initial_data)

    repo = ProductRepository(db=db)
    return repo, db


def make_product_mock(product_data):
    """Create a product-like object with to_dict method."""
    product = MagicMock()
    product.to_dict.return_value = product_data
    return product


def test_get_all_products_returns_empty_list_when_db_file_missing(tmp_path):
    repo, _ = make_product_repo(tmp_path)

    result = repo.get_all()

    assert result == []


def test_get_all_products_returns_saved_products(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": None,
                "document": None,
            },
            {
                "id": "prod-2",
                "description": "Product 2",
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, _ = make_product_repo(tmp_path, initial_data)

    result = repo.get_all()

    assert result == initial_data["products"]


def test_get_by_id_returns_product_when_product_exists(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": None,
                "document": None,
            },
            {
                "id": "prod-2",
                "description": "Product 2",
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, _ = make_product_repo(tmp_path, initial_data)

    result = repo.get_by_id("prod-2")

    assert result == {
        "id": "prod-2",
        "description": "Product 2",
        "image": None,
        "document": None,
    }


def test_get_by_id_returns_none_when_product_does_not_exist(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, _ = make_product_repo(tmp_path, initial_data)

    result = repo.get_by_id("missing-product")

    assert result is None


def test_add_product_persists_product_to_json_db(tmp_path):
    repo, db = make_product_repo(
        tmp_path,
        {
            "products": [],
            "invoices": [],
        },
    )

    product_data = {
        "id": "prod-1",
        "description": "Product 1",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 100.0,
        "alternate": "ALT-001",
        "company": "AirPart",
        "image": None,
        "document": None,
        "timestamp": None,
    }
    product = make_product_mock(product_data)

    result = repo.add(product)

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == [product_data]
    product.to_dict.assert_called_once_with()


def test_delete_product_removes_product_from_json_db(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": None,
                "document": None,
            },
            {
                "id": "prod-2",
                "description": "Product 2",
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, db = make_product_repo(tmp_path, initial_data)

    result = repo.delete("prod-1")

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == [
        {
            "id": "prod-2",
            "description": "Product 2",
            "image": None,
            "document": None,
        },
    ]


def test_delete_product_removes_related_image_and_document_files(tmp_path):
    image_file = tmp_path / "product-image.png"
    document_file = tmp_path / "product-document.pdf"

    image_file.write_bytes(b"fake image content")
    document_file.write_bytes(b"fake document content")

    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": str(image_file),
                "document": str(document_file),
            },
        ],
        "invoices": [],
    }
    repo, db = make_product_repo(tmp_path, initial_data)

    result = repo.delete("prod-1")

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == []
    assert not image_file.exists()
    assert not document_file.exists()


def test_delete_product_ignores_missing_image_and_document_files(tmp_path):
    missing_image = tmp_path / "missing-image.png"
    missing_document = tmp_path / "missing-document.pdf"

    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": str(missing_image),
                "document": str(missing_document),
            },
        ],
        "invoices": [],
    }
    repo, db = make_product_repo(tmp_path, initial_data)

    result = repo.delete("prod-1")

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == []


def test_delete_product_keeps_data_unchanged_when_product_not_found(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, db = make_product_repo(tmp_path, initial_data)

    result = repo.delete("missing-product")

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == initial_data["products"]


def test_update_product_replaces_existing_product(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Old Product",
                "qty": 10,
                "image": None,
                "document": None,
            },
            {
                "id": "prod-2",
                "description": "Another Product",
                "qty": 5,
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, db = make_product_repo(tmp_path, initial_data)

    new_product_data = {
        "id": "prod-1",
        "description": "Updated Product",
        "qty": 20,
        "image": None,
        "document": None,
    }
    new_product = make_product_mock(new_product_data)

    result = repo.update("prod-1", new_product)

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == [
        new_product_data,
        {
            "id": "prod-2",
            "description": "Another Product",
            "qty": 5,
            "image": None,
            "document": None,
        },
    ]
    new_product.to_dict.assert_called_once_with()


def test_update_product_keeps_data_unchanged_when_product_not_found(tmp_path):
    initial_data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Product 1",
                "qty": 10,
                "image": None,
                "document": None,
            },
        ],
        "invoices": [],
    }
    repo, db = make_product_repo(tmp_path, initial_data)

    new_product_data = {
        "id": "missing-product",
        "description": "Updated Product",
        "qty": 20,
        "image": None,
        "document": None,
    }
    new_product = make_product_mock(new_product_data)

    result = repo.update("missing-product", new_product)

    assert result is None

    saved_data = db.load()
    assert saved_data["products"] == initial_data["products"]
    new_product.to_dict.assert_not_called()
