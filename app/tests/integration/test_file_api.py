from io import BytesIO


def test_upload_file_success(client, storage_service, monkeypatch):
    monkeypatch.setattr("app.apis.routes.files.storage_service", storage_service)

    data = {
        "file": (BytesIO(b"%PDF-1.4 test content"), "sample_doc.pdf"),
    }

    resp = client.post(
        "/files/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 201
    json_data = resp.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["category"] == "document"


def test_upload_file_missing_payload(client):
    resp = client.post(
        "/files/upload",
        data={},
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data["success"] is False
    assert json_data["message"] == "No file provided"


def test_upload_file_empty_filename(client):
    data = {
        "file": (BytesIO(b"content"), ""),
    }

    resp = client.post(
        "/files/upload",
        data=data,
        content_type="multipart/form-data",
    )

    assert resp.status_code == 400
    json_data = resp.get_json()
    assert json_data["success"] is False
    assert json_data["message"] == "Empty file."
