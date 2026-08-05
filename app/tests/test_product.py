from io import BytesIO
from unittest.mock import patch

import pandas as pd

# ==============================================================================
# POST /product/search
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_search_product_success(mock_prod_service, client, mock_product_data):
    """Test searching products with valid query return matching products"""
    mock_prod_service.search.return_value = [mock_product_data]

    payload = {"query": "VALVE ASSEMBLY.734-2061.SN-99823.EA.734-2061ALT.Airbus"}

    response = client.post("/product/search", json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["message"] == "search products successfully"
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["part_number"] == "PN-001"


def test_search_product_missing_query(client):
    """Test search fails with 400 when query is missing or empty"""
    response = client.post("/product/search", json={})

    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False


# ==============================================================================
# POST /product/<product_id>/upload_docs
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_upload_docs_success(mock_service, client):
    mock_service.upload_file_docs.return_value = {
        "message": "document uploaded successfuly",
        "document_url": "/tmp/some.pdf",
    }

    data = {
        "document": (BytesIO(b"%PDF-1.4 fake pdf content"), "doc.pdf"),
    }

    resp = client.post(
        "/product/prod-1/upload_docs",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    j = resp.get_json()
    assert j["success"] is True
    assert j["message"] == "document uploaded successfuly"


def test_upload_docs_missing_file(client):
    resp = client.post(
        "/product/prod-1/upload_docs",
        data={},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    j = resp.get_json()
    assert j["success"] is False
    assert j["message"] == "No document file provided"
    assert j["errors"]["document"] == "File is required"


# ==============================================================================
# POST /product/<id_product>/upload_image
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_upload_image_success(mock_service, client):
    mock_service.upload_file_image.return_value = {
        "message": "Image uploaded successfuly",
        "image_url": "/tmp/some-image.png",
    }

    data = {
        "image": (BytesIO(b"fake-image-bytes"), "photo.png"),
    }

    resp = client.post(
        "/product/prod-1/upload_image",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    j = resp.get_json()
    assert j["success"] is True
    assert j["message"] == "Image uploaded successfuly"

    assert "data" not in j


def test_upload_image_missing_file(client):
    resp = client.post(
        "/product/prod-1/upload_image",
        data={},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    j = resp.get_json()
    assert j["success"] is False
    assert j["message"] == "No image file provided"
    assert j["errors"]["image"] == "File is required"


def test_upload_image_empty_filename(client):
    data = {
        "image": (BytesIO(b"abc"), ""),  # filename == ""
    }

    resp = client.post(
        "/product/prod-1/upload_image",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    j = resp.get_json()
    assert j["success"] is False
    assert j["message"] == "Empty file."
    assert j["errors"]["image"] == "Invalid file name"


@patch("app.apis.routes.product.product_service")
def test_upload_image_service_error_returns_400(mock_service, client):
    mock_service.upload_file_image.return_value = {
        "error": "Invalid file or file type not allowed"
    }

    data = {
        "image": (BytesIO(b"abc"), "not_allowed.bmp"),
    }

    resp = client.post(
        "/product/prod-1/upload_image",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    j = resp.get_json()
    assert j["success"] is False
    assert j["errors"] == "Invalid file or file type not allowed"


@patch("app.apis.routes.product.product_service")
def test_upload_image_unexpected_service_response_returns_500(mock_service, client):
    mock_service.upload_file_image.return_value = None  # not a dict

    data = {
        "image": (BytesIO(b"abc"), "photo.png"),
    }

    resp = client.post(
        "/product/prod-1/upload_image",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 500
    j = resp.get_json()
    assert j["success"] is False
    assert j["message"] == "Internal backend error"


# ==============================================================================
# POST /product/add_from_excel (Integration style using in-memory excel)
# ==============================================================================


@patch("app.apis.routes.product.product_service.repo")
def test_add_from_excel_success(mock_repo, client):
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

    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Sheet1", index=False)
    excel_buffer.seek(0)

    data = {
        "excel_file": (excel_buffer, "products.xlsx"),
    }

    resp = client.post(
        "/product/add_from_excel",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 200
    j = resp.get_json()
    assert j["success"] is True
    assert j["message"] == "Extract excel file successfully"
    assert mock_repo.add.called


# ==============================================================================
# GET /products
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_get_all_products_success(mock_service, client):
    mock_products = [
        {
            "id": "prod-1",
            "description": "Test Product 1",
            "part_number": "PN-001",
            "serial_number": "SN-001",
            "qty": 10,
            "unit": "PCS",
            "price": 100.0,
            "alternate": "ALT-001",
            "company": "Test Company",
            "document": None,
            "image": None,
            "timestamp": None,
        },
        {
            "id": "prod-2",
            "description": "Test Product 2",
            "part_number": "PN-002",
            "serial_number": "SN-002",
            "qty": 5,
            "unit": "PCS",
            "price": 200.0,
            "alternate": "ALT-002",
            "company": "Test Company",
            "document": None,
            "image": None,
            "timestamp": None,
        },
    ]

    mock_service.getallproduct.return_value = mock_products

    resp = client.get("/products")

    assert resp.status_code == 200
    j = resp.get_json()

    assert j["success"] is True
    assert j["message"] == "Product list successfully received."
    assert j["data"] == mock_products

    mock_service.getallproduct.assert_called_once_with()


@patch("app.apis.routes.product.product_service")
def test_get_all_products_internal_server_error(mock_service, client):
    mock_service.getallproduct.side_effect = Exception("DB error")

    resp = client.get("/products")

    assert resp.status_code == 500
    j = resp.get_json()

    assert j["success"] is False
    assert j["message"] == "Internal server error while retrieving product list."

    mock_service.getallproduct.assert_called_once_with()


# ==============================================================================
# GET /product/<id_product>
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_get_a_product_success(mock_service, client):
    mock_product = {
        "id": "prod-1",
        "description": "Test Product",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 100.0,
        "alternate": "ALT-001",
        "company": "Test Company",
        "document": None,
        "image": None,
        "timestamp": None,
    }

    mock_service.get_a_product_by_id.return_value = mock_product

    resp = client.get("/product/prod-1")

    assert resp.status_code == 200
    j = resp.get_json()

    assert j["success"] is True
    assert j["message"] == "Product received successfully."
    assert j["data"] == mock_product

    mock_service.get_a_product_by_id.assert_called_once_with("prod-1")


@patch("app.apis.routes.product.product_service")
def test_get_a_product_not_found(mock_service, client):
    mock_service.get_a_product_by_id.return_value = None

    resp = client.get("/product/not-found-id")

    assert resp.status_code == 404
    j = resp.get_json()

    assert j["success"] is False
    assert j["message"] == "Product with ID 'not-found-id' not found."
    assert j["errors"]["id"] == "Product with ID 'not-found-id' not found."

    mock_service.get_a_product_by_id.assert_called_once_with("not-found-id")


@patch("app.apis.routes.product.product_service")
def test_get_a_product_internal_server_error(mock_service, client):
    mock_service.get_a_product_by_id.side_effect = Exception("DB error")

    resp = client.get("/product/prod-1")

    assert resp.status_code == 500
    j = resp.get_json()

    assert j["success"] is False
    assert j["message"] == "Internal server error while getting product."

    mock_service.get_a_product_by_id.assert_called_once_with("prod-1")


# ==============================================================================
# POST /product/add
# ==============================================================================


@patch("app.apis.routes.product.product_service")
def test_add_product_success(mock_service, client):
    payload = {
        "id": "prod-1",
        "description": "Test Product",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 100.0,
        "alternate": "ALT-001",
        "company": "Test Company",
        "document": None,
        "image": None,
        "timestamp": None,
    }

    mock_service.addproduct.return_value = None

    resp = client.post("/product/add", json=payload)

    assert resp.status_code == 201
    j = resp.get_json()

    assert j["success"] is True
    assert j["message"] == "Product added successfully."

    assert j["data"]["id"] == payload["id"]
    assert j["data"]["description"] == payload["description"]
    assert j["data"]["part_number"] == payload["part_number"]
    assert j["data"]["serial_number"] == payload["serial_number"]
    assert j["data"]["qty"] == payload["qty"]
    assert j["data"]["unit"] == payload["unit"]
    assert j["data"]["price"] == payload["price"]
    assert j["data"]["alternate"] == payload["alternate"]
    assert j["data"]["company"] == payload["company"]
    assert j["data"]["document"] == payload["document"]
    assert j["data"]["image"] == payload["image"]

    assert "timestamp" in j["data"]
    assert j["data"]["timestamp"] is not None
    assert isinstance(j["data"]["timestamp"], (int, float))

    mock_service.addproduct.assert_called_once()

    added_product = mock_service.addproduct.call_args.args[0]
    assert added_product.to_dict()["id"] == payload["id"]
    assert added_product.to_dict()["description"] == payload["description"]


@patch("app.apis.routes.product.product_service")
def test_add_product_internal_server_error(mock_service, client):
    payload = {
        "id": "prod-1",
        "description": "Test Product",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 100.0,
        "alternate": "ALT-001",
        "company": "Test Company",
        "document": None,
        "image": None,
        "timestamp": None,
    }

    mock_service.addproduct.side_effect = Exception("DB error")

    resp = client.post("/product/add", json=payload)

    assert resp.status_code == 500
    j = resp.get_json()

    assert j["success"] is False
    assert j["message"] == "Internal server error while adding product."

    mock_service.addproduct.assert_called_once()
