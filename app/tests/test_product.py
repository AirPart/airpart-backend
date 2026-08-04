from io import BytesIO
from unittest.mock import patch

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
    assert json_data["data"][0]["part_number"] == "734-2061"


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
