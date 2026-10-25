"""Routes for centralized file management."""

import os

from flask import Blueprint, request

from app.apis.deps import json_response
from app.services.files.storage import StorageService

file_bp = Blueprint("file", __name__)
storage_service = StorageService()

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FILE_YAML = os.path.join(DIR_PATH, "docs", "files", "upload.yml")


@file_bp.route("/files/upload", methods=["POST"])
# @swag_from(UPLOAD_FILE_YAML)
def upload_file() -> tuple:
    """
    Unified endpoint to upload any file (Image or PDF).
    Automatically detects category and stores in the correct server directory.
    """
    if "file" not in request.files:
        return (
            json_response(
                False,
                "No file provided",
                errors={"file": "File field is required in form-data"},
            ),
            400,
        )

    file_obj = request.files["file"]

    if file_obj.filename == "":
        return (
            json_response(
                False,
                "Empty file.",
                errors={"file": "Invalid or empty filename"},
            ),
            400,
        )

    result = storage_service.save_file(file_obj)

    if not isinstance(result, dict):
        return (
            json_response(False, "Internal backend error during file upload"),
            500,
        )

    if "error" in result:
        return (
            json_response(
                False,
                message=result["error"],
                errors={"file": result["error"]},
            ),
            400,
        )

    return (
        json_response(
            True,
            message=f"{result['category'].capitalize()} uploaded successfully",
            data={
                "url": result["file_path"],
                "filename": result["filename"],
                "category": result["category"],
            },
        ),
        201,
    )
