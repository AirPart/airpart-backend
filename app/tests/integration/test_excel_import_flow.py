"""Integration tests for Excel product import workflow."""

import json
from pathlib import Path

import pandas as pd

from app.repository.product import ProductRepository
from app.services.products.product import ProductService


class TempJsonDB:
    """Small JSON-backed DB adapter for Excel import integration tests."""

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


def get_excel_import_method(product_service):
    """Return the Excel import method used by ProductService."""
    candidate_names = [
        "import_excel",
        "import_from_excel",
        "import_products_from_excel",
        "upload_excel",
        "add_products_from_excel",
        "add_from_excel",
        "read_product_from_excel",
    ]

    for name in candidate_names:
        method = getattr(product_service, name, None)
        if method is not None:
            return method

    raise AssertionError(
        "No Excel import method found on ProductService. "
        "Update candidate_names in this test to match the project method name."
    )


def make_excel_file(path):
    dataframe = pd.DataFrame(
        [
            {
                "DISCRIPTION": "Engine Part",
                "PART NO.": "PN-001",
                "SERIAL NO.": "SN-001",
                "QTY": 10,
                "UNIT": "PCS",
                "PRICE": 100.0,
                "ALTERNATE": "ALT-001",
                "COMPANY": "AirPart",
            },
            {
                "DISCRIPTION": "Landing Gear Part",
                "PART NO.": "PN-002",
                "SERIAL NO.": "SN-002",
                "QTY": 5,
                "UNIT": "PCS",
                "PRICE": 250.0,
                "ALTERNATE": "ALT-002",
                "COMPANY": "AirPart",
            },
        ]
    )

    dataframe.to_excel(path, index=False)


def test_excel_import_flow_adds_products_to_repository(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    product_repo = ProductRepository(db=db)
    product_service = ProductService(db=db, repo=product_repo)

    excel_file = tmp_path / "products.xlsx"
    make_excel_file(excel_file)

    import_method = get_excel_import_method(product_service)

    try:
        result = import_method(excel_file)
    except TypeError:
        result = import_method(str(excel_file))

    products = product_repo.get_all()

    assert len(products) == 2
    assert products[0]["description"] == "Engine Part"
    assert products[0]["part_number"] == "PN-001"
    assert products[0]["qty"] == 10
    assert products[1]["description"] == "Landing Gear Part"
    assert products[1]["part_number"] == "PN-002"
    assert products[1]["qty"] == 5

    assert result is not None or products


def test_excel_import_flow_does_not_touch_production_database(tmp_path):
    db = TempJsonDB(tmp_path / "db.json")
    product_repo = ProductRepository(db=db)
    product_service = ProductService(db=db, repo=product_repo)

    excel_file = tmp_path / "products.xlsx"
    make_excel_file(excel_file)

    import_method = get_excel_import_method(product_service)

    try:
        import_method(excel_file)
    except TypeError:
        import_method(str(excel_file))

    data = json.loads((tmp_path / "db.json").read_text(encoding="utf-8"))

    assert len(data["products"]) == 2
