from io import BytesIO
from pathlib import Path

from werkzeug.datastructures import FileStorage


def test_detect_category_image(storage_service):
    assert storage_service.detect_category("photo.png") == "image"
    assert storage_service.detect_category("avatar.JPG") == "image"


def test_detect_category_document(storage_service):
    assert storage_service.detect_category("manual.pdf") == "document"
    assert storage_service.detect_category("sheet.xlsx") is None


def test_detect_category_invalid(storage_service):
    assert storage_service.detect_category("script.sh") is None


def test_save_file_success_image(storage_service):
    file_obj = FileStorage(
        stream=BytesIO(b"fake image bytes"),
        filename="test_photo.png",
        content_type="image/png",
    )

    result = storage_service.save_file(file_obj)

    assert "error" not in result
    assert result["category"] == "image"
    assert result["filename"].endswith(".png")
    assert Path(result["file_path"]).is_file()
    assert Path(result["file_path"]).parent.name == "images"


def test_save_file_success_document(storage_service):
    file_obj = FileStorage(
        stream=BytesIO(b"%PDF-1.4 test content"),
        filename="manual.pdf",
        content_type="application/pdf",
    )

    result = storage_service.save_file(file_obj)

    assert "error" not in result
    assert result["category"] == "document"
    assert result["filename"].endswith(".pdf")
    assert Path(result["file_path"]).is_file()
    assert Path(result["file_path"]).parent.name == "documents"


def test_save_file_unsupported_extension(storage_service):
    file_obj = FileStorage(
        stream=BytesIO(b"binary content"),
        filename="virus.exe",
    )

    result = storage_service.save_file(file_obj)

    assert "error" in result
    assert "Unsupported file type" in result["error"]
