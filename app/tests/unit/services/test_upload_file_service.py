"""Unit/integration-style tests for UploadFileAPI."""

from io import BytesIO
from unittest.mock import MagicMock, patch

from app.services.products.upload_file import UploadFileAPI


def make_upload_api():
    """Create UploadFileAPI with mocked db."""
    mock_db = MagicMock()
    upload_api = UploadFileAPI(db=mock_db)
    return upload_api, mock_db


# ==============================================================================
# allowed_file_image
# ==============================================================================


def test_allowed_file_image_accepts_supported_extensions():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_image("image.png") is True
    assert upload_api.allowed_file_image("image.jpg") is True
    assert upload_api.allowed_file_image("image.jpeg") is True
    assert upload_api.allowed_file_image("image.gif") is True


def test_allowed_file_image_is_case_insensitive_for_extension():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_image("image.PNG") is True
    assert upload_api.allowed_file_image("image.JPG") is True


def test_allowed_file_image_rejects_unsupported_extensions():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_image("image.bmp") is False
    assert upload_api.allowed_file_image("image.pdf") is False


def test_allowed_file_image_rejects_filename_without_extension():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_image("image") is False


# ==============================================================================
# allowed_file_docs
# ==============================================================================


def test_allowed_file_docs_accepts_pdf_extension():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_docs("document.pdf") is True


def test_allowed_file_docs_is_case_insensitive_for_extension():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_docs("document.PDF") is True


def test_allowed_file_docs_rejects_non_pdf_extensions():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_docs("document.docx") is False
    assert upload_api.allowed_file_docs("document.txt") is False
    assert upload_api.allowed_file_docs("image.png") is False


def test_allowed_file_docs_rejects_filename_without_extension():
    upload_api, _ = make_upload_api()

    assert upload_api.allowed_file_docs("document") is False


# ==============================================================================
# generate_unique_filename
# ==============================================================================


@patch("app.services.products.upload_file.uuid.uuid4")
def test_generate_unique_filename_returns_uuid_with_original_extension(mock_uuid4):
    upload_api, _ = make_upload_api()

    mock_uuid4.return_value = "fixed-uuid"

    result = upload_api.generate_unique_filename("photo.PNG")

    assert result == "fixed-uuid.png"
    mock_uuid4.assert_called_once_with()


# ==============================================================================
# upload_image
# ==============================================================================


@patch("app.services.products.upload_file.uuid.uuid4")
def test_upload_image_saves_file_updates_product_and_returns_image_url(
    mock_uuid4,
    tmp_path,
    monkeypatch,
):
    image_dir = tmp_path / "images"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        str(image_dir),
    )

    mock_uuid4.return_value = "image-uuid"

    upload_api, mock_db = make_upload_api()

    db_data = {
        "products": [
            {
                "id": "prod-1",
                "image": None,
                "document": None,
            }
        ],
        "invoices": [],
    }
    mock_db.load.return_value = db_data

    file_data = BytesIO(b"fake image content")

    result = upload_api.upload_image(
        id_product="prod-1",
        file_data=file_data,
        filename="photo.png",
    )

    expected_filepath = image_dir / "image-uuid.png"

    assert result == {
        "message": "Image uploaded successfuly",
        "image_url": str(expected_filepath),
    }

    assert expected_filepath.exists()
    assert expected_filepath.read_bytes() == b"fake image content"

    assert db_data["products"][0]["image"] == str(expected_filepath)
    mock_db.load.assert_called_once_with()
    mock_db.save.assert_called_once_with(db_data)


def test_upload_image_creates_image_directory_when_missing(tmp_path, monkeypatch):
    image_dir = tmp_path / "new-images"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        str(image_dir),
    )

    upload_api, mock_db = make_upload_api()

    db_data = {
        "products": [
            {
                "id": "prod-1",
                "image": None,
                "document": None,
            }
        ],
        "invoices": [],
    }
    mock_db.load.return_value = db_data

    result = upload_api.upload_image(
        id_product="prod-1",
        file_data=BytesIO(b"fake image content"),
        filename="photo.png",
    )

    assert "image_url" in result
    assert image_dir.exists()
    assert image_dir.is_dir()


def test_upload_image_returns_error_for_empty_filename(tmp_path, monkeypatch):
    image_dir = tmp_path / "images"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        str(image_dir),
    )

    upload_api, mock_db = make_upload_api()

    result = upload_api.upload_image(
        id_product="prod-1",
        file_data=BytesIO(b"fake image content"),
        filename="",
    )

    assert result == {"error": "Invalid file or file type not allowed"}
    mock_db.load.assert_not_called()
    mock_db.save.assert_not_called()


def test_upload_image_returns_error_for_invalid_extension(tmp_path, monkeypatch):
    image_dir = tmp_path / "images"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        str(image_dir),
    )

    upload_api, mock_db = make_upload_api()

    result = upload_api.upload_image(
        id_product="prod-1",
        file_data=BytesIO(b"fake image content"),
        filename="photo.bmp",
    )

    assert result == {"error": "Invalid file or file type not allowed"}
    mock_db.load.assert_not_called()
    mock_db.save.assert_not_called()


@patch("app.services.products.upload_file.uuid.uuid4")
def test_upload_image_removes_uploaded_file_when_product_not_found(
    mock_uuid4,
    tmp_path,
    monkeypatch,
):
    image_dir = tmp_path / "images"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        str(image_dir),
    )

    mock_uuid4.return_value = "image-uuid"

    upload_api, mock_db = make_upload_api()

    db_data = {
        "products": [
            {
                "id": "another-product",
                "image": None,
                "document": None,
            }
        ],
        "invoices": [],
    }
    mock_db.load.return_value = db_data

    result = upload_api.upload_image(
        id_product="missing-product",
        file_data=BytesIO(b"fake image content"),
        filename="photo.png",
    )

    expected_filepath = image_dir / "image-uuid.png"

    assert result == {"error": "Product with id missing-product not found."}
    assert not expected_filepath.exists()

    mock_db.load.assert_called_once_with()
    mock_db.save.assert_not_called()


@patch("app.services.products.upload_file.uuid.uuid4")
def test_upload_image_removes_file_and_returns_error_when_file_read_fails(
    mock_uuid4,
    tmp_path,
    monkeypatch,
):
    image_dir = tmp_path / "images"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        str(image_dir),
    )

    mock_uuid4.return_value = "image-uuid"

    upload_api, mock_db = make_upload_api()

    file_data = MagicMock()
    file_data.read.side_effect = Exception("read failed")

    result = upload_api.upload_image(
        id_product="prod-1",
        file_data=file_data,
        filename="photo.png",
    )

    expected_filepath = image_dir / "image-uuid.png"

    assert result == {"error": "Failed to process upload: read failed"}
    assert not expected_filepath.exists()

    mock_db.load.assert_not_called()
    mock_db.save.assert_not_called()


def test_upload_image_exits_when_image_directory_config_is_missing(monkeypatch):
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_image",
        None,
    )

    upload_api, _ = make_upload_api()

    try:
        upload_api.upload_image(
            id_product="prod-1",
            file_data=BytesIO(b"fake image content"),
            filename="photo.png",
        )
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("SystemExit was not raised")


# ==============================================================================
# upload_docs
# ==============================================================================


@patch("app.services.products.upload_file.uuid.uuid4")
def test_upload_docs_saves_file_updates_product_and_returns_document_url(
    mock_uuid4,
    tmp_path,
    monkeypatch,
):
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        str(docs_dir),
    )

    mock_uuid4.return_value = "docs-uuid"

    upload_api, mock_db = make_upload_api()

    db_data = {
        "products": [
            {
                "id": "prod-1",
                "image": None,
                "document": None,
            }
        ],
        "invoices": [],
    }
    mock_db.load.return_value = db_data

    file_data = BytesIO(b"%PDF-1.4 fake pdf content")

    result = upload_api.upload_docs(
        id_product="prod-1",
        file_data=file_data,
        filename="manual.pdf",
    )

    expected_filepath = docs_dir / "docs-uuid.pdf"

    assert result == {
        "message": "document uploaded successfuly",
        "document_url": str(expected_filepath),
    }

    assert expected_filepath.exists()
    assert expected_filepath.read_bytes() == b"%PDF-1.4 fake pdf content"

    assert db_data["products"][0]["document"] == str(expected_filepath)
    mock_db.load.assert_called_once_with()
    mock_db.save.assert_called_once_with(db_data)


def test_upload_docs_creates_docs_directory_when_missing(tmp_path, monkeypatch):
    docs_dir = tmp_path / "new-docs"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        str(docs_dir),
    )

    upload_api, mock_db = make_upload_api()

    db_data = {
        "products": [
            {
                "id": "prod-1",
                "image": None,
                "document": None,
            }
        ],
        "invoices": [],
    }
    mock_db.load.return_value = db_data

    result = upload_api.upload_docs(
        id_product="prod-1",
        file_data=BytesIO(b"%PDF-1.4 fake pdf content"),
        filename="manual.pdf",
    )

    assert "document_url" in result
    assert docs_dir.exists()
    assert docs_dir.is_dir()


def test_upload_docs_returns_error_for_empty_filename(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        str(docs_dir),
    )

    upload_api, mock_db = make_upload_api()

    result = upload_api.upload_docs(
        id_product="prod-1",
        file_data=BytesIO(b"%PDF-1.4 fake pdf content"),
        filename="",
    )

    assert result == {"error": "Invalid file or file type not allowed"}
    mock_db.load.assert_not_called()
    mock_db.save.assert_not_called()


def test_upload_docs_returns_error_for_invalid_extension(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        str(docs_dir),
    )

    upload_api, mock_db = make_upload_api()

    result = upload_api.upload_docs(
        id_product="prod-1",
        file_data=BytesIO(b"fake content"),
        filename="manual.docx",
    )

    assert result == {"error": "Invalid file or file type not allowed"}
    mock_db.load.assert_not_called()
    mock_db.save.assert_not_called()


@patch("app.services.products.upload_file.uuid.uuid4")
def test_upload_docs_removes_uploaded_file_when_product_not_found(
    mock_uuid4,
    tmp_path,
    monkeypatch,
):
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        str(docs_dir),
    )

    mock_uuid4.return_value = "docs-uuid"

    upload_api, mock_db = make_upload_api()

    db_data = {
        "products": [
            {
                "id": "another-product",
                "image": None,
                "document": None,
            }
        ],
        "invoices": [],
    }
    mock_db.load.return_value = db_data

    result = upload_api.upload_docs(
        id_product="missing-product",
        file_data=BytesIO(b"%PDF-1.4 fake pdf content"),
        filename="manual.pdf",
    )

    expected_filepath = docs_dir / "docs-uuid.pdf"

    assert result == {"error": "Product with id missing-product not found."}
    assert not expected_filepath.exists()

    mock_db.load.assert_called_once_with()
    mock_db.save.assert_not_called()


@patch("app.services.products.upload_file.uuid.uuid4")
def test_upload_docs_removes_file_and_returns_error_when_file_read_fails(
    mock_uuid4,
    tmp_path,
    monkeypatch,
):
    docs_dir = tmp_path / "docs"
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        str(docs_dir),
    )

    mock_uuid4.return_value = "docs-uuid"

    upload_api, mock_db = make_upload_api()

    file_data = MagicMock()
    file_data.read.side_effect = Exception("read failed")

    result = upload_api.upload_docs(
        id_product="prod-1",
        file_data=file_data,
        filename="manual.pdf",
    )

    expected_filepath = docs_dir / "docs-uuid.pdf"

    assert result == {"error": "Failed to process upload: read failed"}
    assert not expected_filepath.exists()

    mock_db.load.assert_not_called()
    mock_db.save.assert_not_called()


def test_upload_docs_exits_when_docs_directory_config_is_missing(monkeypatch):
    monkeypatch.setattr(
        "app.services.products.upload_file.db_product_docs",
        None,
    )

    upload_api, _ = make_upload_api()

    try:
        upload_api.upload_docs(
            id_product="prod-1",
            file_data=BytesIO(b"%PDF-1.4 fake pdf content"),
            filename="manual.pdf",
        )
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("SystemExit was not raised")
