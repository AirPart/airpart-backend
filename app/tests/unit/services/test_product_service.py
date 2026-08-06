"""Unit tests for ProductService."""

from unittest.mock import MagicMock, patch

import pandas as pd

from app.services.products.product import ProductService


def make_service():
    """Create ProductService with mocked db and repository."""
    mock_db = MagicMock()
    mock_repo = MagicMock()
    service = ProductService(db=mock_db, repo=mock_repo)
    return service, mock_db, mock_repo


# ==============================================================================
# Basic repository delegation
# ==============================================================================


def test_get_all_products_returns_repo_products():
    service, _, mock_repo = make_service()

    expected_products = [
        {"id": "prod-1", "description": "Product 1"},
        {"id": "prod-2", "description": "Product 2"},
    ]
    mock_repo.get_all.return_value = expected_products

    result = service.getallproduct()

    assert result == expected_products
    mock_repo.get_all.assert_called_once_with()


def test_get_a_product_by_id_returns_repo_product():
    service, _, mock_repo = make_service()

    expected_product = {"id": "prod-1", "description": "Product 1"}
    mock_repo.get_by_id.return_value = expected_product

    result = service.get_a_product_by_id("prod-1")

    assert result == expected_product
    mock_repo.get_by_id.assert_called_once_with(product_id="prod-1")


def test_get_a_product_by_id_returns_none_when_product_not_found():
    service, _, mock_repo = make_service()

    mock_repo.get_by_id.return_value = None

    result = service.get_a_product_by_id("missing-product")

    assert result is None
    mock_repo.get_by_id.assert_called_once_with(product_id="missing-product")


def test_add_product_calls_repository_add():
    service, _, mock_repo = make_service()

    product = MagicMock()

    result = service.addproduct(product)

    assert result is None
    mock_repo.add.assert_called_once_with(product=product)


def test_remove_product_calls_repository_delete():
    service, _, mock_repo = make_service()

    result = service.rmproduct("prod-1")

    assert result is None
    mock_repo.delete.assert_called_once_with(product_id="prod-1")


def test_update_product_calls_repository_update():
    service, _, mock_repo = make_service()

    new_product = MagicMock()

    result = service.putproduct("prod-1", new_product)

    assert result is None
    mock_repo.update.assert_called_once_with(
        product_id="prod-1",
        new_product=new_product,
    )


# ==============================================================================
# Search workflow
# ==============================================================================


@patch("app.services.products.product.SearchAPI")
def test_search_uses_repository_products_and_search_api(mock_search_api_class):
    service, _, mock_repo = make_service()

    products = [
        {"id": "prod-1", "part_number": "PN-001"},
        {"id": "prod-2", "part_number": "PN-002"},
    ]
    expected_result = [{"id": "prod-1", "part_number": "PN-001"}]

    mock_repo.get_all.return_value = products

    mock_search_api = MagicMock()
    mock_search_api.search_products.return_value = expected_result
    mock_search_api_class.return_value = mock_search_api

    result = service.search("PN-001")

    assert result == expected_result

    mock_repo.get_all.assert_called_once_with()
    mock_search_api_class.assert_called_once_with("PN-001")
    mock_search_api.search_products.assert_called_once_with(products)


# ==============================================================================
# Upload file workflow
# ==============================================================================


@patch("app.services.products.product.UploadFileAPI")
def test_upload_file_image_uses_upload_file_api(mock_upload_file_api_class):
    service, mock_db, _ = make_service()

    file_data = MagicMock()
    expected_result = {
        "message": "Image uploaded successfuly",
        "image_url": "/tmp/product/photo.png",
    }

    mock_upload_api = MagicMock()
    mock_upload_api.upload_image.return_value = expected_result
    mock_upload_file_api_class.return_value = mock_upload_api

    result = service.upload_file_image(
        idproduct="prod-1",
        file_data=file_data,
        filename="photo.png",
    )

    assert result == expected_result

    mock_upload_file_api_class.assert_called_once_with(mock_db)
    mock_upload_api.upload_image.assert_called_once_with(
        "prod-1",
        file_data,
        "photo.png",
    )


@patch("app.services.products.product.UploadFileAPI")
def test_upload_file_docs_uses_upload_file_api(mock_upload_file_api_class):
    service, mock_db, _ = make_service()

    file_data = MagicMock()
    expected_result = {
        "message": "document uploaded successfuly",
        "document_url": "/tmp/product/doc.pdf",
    }

    mock_upload_api = MagicMock()
    mock_upload_api.upload_docs.return_value = expected_result
    mock_upload_file_api_class.return_value = mock_upload_api

    result = service.upload_file_docs(
        idproduct="prod-1",
        file_data=file_data,
        filename="doc.pdf",
    )

    assert result == expected_result

    mock_upload_file_api_class.assert_called_once_with(mock_db)
    mock_upload_api.upload_docs.assert_called_once_with(
        "prod-1",
        file_data,
        "doc.pdf",
    )


# ==============================================================================
# Excel import workflow
# ==============================================================================


@patch("app.services.products.product.pd.read_excel")
def test_read_product_from_excel_creates_products_and_adds_to_repo(mock_read_excel):
    service, _, mock_repo = make_service()

    df = pd.DataFrame(
        [
            {
                "DISCRIPTION": "Engine Part",
                "PART NO.": "ENG-101",
                "SERIAL NO.": "SN-999",
                "QTY": 5,
                "UNIT": "PCS",
                "PRICE": 120.5,
                "ALTERNATE": "ALT-101",
                "COMPANY": "AirPart Co",
            }
        ]
    )

    mock_read_excel.return_value = {"Sheet1": df}

    excel_file = MagicMock()

    result = service.read_product_from_excel(excel_file)

    assert result is None
    mock_read_excel.assert_called_once_with(excel_file, sheet_name=None)
    mock_repo.add.assert_called_once()

    added_product = mock_repo.add.call_args.args[0]
    added_product_data = added_product.to_dict()

    assert added_product_data["description"] == "Engine Part"
    assert added_product_data["part_number"] == "ENG-101"
    assert added_product_data["serial_number"] == "SN-999"
    assert added_product_data["qty"] == 5
    assert added_product_data["unit"] == "PCS"
    assert added_product_data["price"] == 120.5
    assert added_product_data["alternate"] == "ALT-101"
    assert added_product_data["company"] == "AirPart Co"


@patch("app.services.products.product.pd.read_excel")
def test_read_product_from_excel_uses_default_values_for_missing_cells(
    mock_read_excel,
):
    service, _, mock_repo = make_service()

    df = pd.DataFrame(
        [
            {
                "DISCRIPTION": None,
                "PART NO.": None,
                "SERIAL NO.": None,
                "QTY": None,
                "UNIT": None,
                "PRICE": None,
                "ALTERNATE": None,
                "COMPANY": None,
            }
        ]
    )

    mock_read_excel.return_value = {"Sheet1": df}

    service.read_product_from_excel(MagicMock())

    mock_repo.add.assert_called_once()

    added_product = mock_repo.add.call_args.args[0]
    added_product_data = added_product.to_dict()

    assert added_product_data["description"] == "NA"
    assert added_product_data["part_number"] == "NA"
    assert added_product_data["serial_number"] == "NA"
    assert added_product_data["qty"] == "NA"
    assert added_product_data["unit"] == "NA"
    assert added_product_data["price"] == 0.0
    assert added_product_data["alternate"] == "NA"
    assert added_product_data["company"] == "NA"


@patch("app.services.products.product.pd.read_excel")
def test_read_product_from_excel_imports_products_from_multiple_sheets(
    mock_read_excel,
):
    service, _, mock_repo = make_service()

    sheet_one = pd.DataFrame(
        [
            {
                "DISCRIPTION": "Part A",
                "PART NO.": "A-001",
                "SERIAL NO.": "SN-A",
                "QTY": 2,
                "UNIT": "PCS",
                "PRICE": 10,
                "ALTERNATE": "ALT-A",
                "COMPANY": "Company A",
            }
        ]
    )

    sheet_two = pd.DataFrame(
        [
            {
                "DISCRIPTION": "Part B",
                "PART NO.": "B-001",
                "SERIAL NO.": "SN-B",
                "QTY": 3,
                "UNIT": "PCS",
                "PRICE": 20,
                "ALTERNATE": "ALT-B",
                "COMPANY": "Company B",
            }
        ]
    )

    mock_read_excel.return_value = {
        "Sheet1": sheet_one,
        "Sheet2": sheet_two,
    }

    service.read_product_from_excel(MagicMock())

    assert mock_repo.add.call_count == 2

    first_product = mock_repo.add.call_args_list[0].args[0].to_dict()
    second_product = mock_repo.add.call_args_list[1].args[0].to_dict()

    assert first_product["part_number"] == "A-001"
    assert second_product["part_number"] == "B-001"


# ==============================================================================
# Quantity workflow
# ==============================================================================


def test_decrease_qty_decreases_product_quantity_and_saves_db():
    service, mock_db, _ = make_service()

    db_data = {
        "products": [
            {"id": "prod-1", "qty": 10},
            {"id": "prod-2", "qty": 5},
        ]
    }

    mock_db.load.return_value = db_data

    result = service.decrease_qty(product_id="prod-1", amount=3)

    assert result is None
    assert db_data["products"][0]["qty"] == 7
    assert db_data["products"][1]["qty"] == 5

    mock_db.load.assert_called_once_with()
    mock_db.save.assert_called_once_with(db_data)


def test_increase_qty_increases_product_quantity_and_saves_db():
    service, mock_db, _ = make_service()

    db_data = {
        "products": [
            {"id": "prod-1", "qty": 10},
            {"id": "prod-2", "qty": 5},
        ]
    }

    mock_db.load.return_value = db_data

    result = service.increase_qty(product_id="prod-2", amount=4)

    assert result is None
    assert db_data["products"][0]["qty"] == 10
    assert db_data["products"][1]["qty"] == 9

    mock_db.load.assert_called_once_with()
    mock_db.save.assert_called_once_with(db_data)


def test_decrease_qty_keeps_data_unchanged_when_product_not_found():
    service, mock_db, _ = make_service()

    db_data = {
        "products": [
            {"id": "prod-1", "qty": 10},
        ]
    }

    mock_db.load.return_value = db_data

    service.decrease_qty(product_id="missing-product", amount=3)

    assert db_data["products"][0]["qty"] == 10

    mock_db.load.assert_called_once_with()
    mock_db.save.assert_called_once_with(db_data)


def test_increase_qty_keeps_data_unchanged_when_product_not_found():
    service, mock_db, _ = make_service()

    db_data = {
        "products": [
            {"id": "prod-1", "qty": 10},
        ]
    }

    mock_db.load.return_value = db_data

    service.increase_qty(product_id="missing-product", amount=3)

    assert db_data["products"][0]["qty"] == 10

    mock_db.load.assert_called_once_with()
    mock_db.save.assert_called_once_with(db_data)
