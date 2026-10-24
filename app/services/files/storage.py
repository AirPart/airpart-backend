"""Central file storage service for managing uploads across the application."""

from __future__ import annotations

import os
import uuid

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.core.config import db_product_docs, db_product_image


class FileCategory:
    IMAGE = "image"
    DOCUMENT = "document"


class StorageService:
    """Handles saving, categorizing, and validating uploaded files on disk."""

    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf"}

    def __init__(
        self,
        image_dir: str | None = db_product_image,
        docs_dir: str | None = db_product_docs,
    ) -> None:
        self.image_dir = image_dir
        self.docs_dir = docs_dir

    def get_extension(self, filename: str) -> str:
        """Extract sanitized lowercase file extension."""
        if not filename or "." not in filename:
            return ""
        return filename.rsplit(".", 1)[1].lower()

    def detect_category(self, filename: str) -> str | None:
        """
        Detect file category (image or document) based on its extension.
        Returns FileCategory.IMAGE, FileCategory.DOCUMENT, or None if not supported.
        """
        ext = self.get_extension(filename)
        if ext in self.ALLOWED_IMAGE_EXTENSIONS:
            return FileCategory.IMAGE
        if ext in self.ALLOWED_DOCUMENT_EXTENSIONS:
            return FileCategory.DOCUMENT
        return None

    def get_target_directory(self, category: str) -> str:
        """Resolve target storage directory based on category."""
        if category == FileCategory.IMAGE:
            if not self.image_dir:
                raise ValueError("Images storage directory is not configured.")
            return self.image_dir

        if category == FileCategory.DOCUMENT:
            if not self.docs_dir:
                raise ValueError("Documents storage directory is not configured.")
            return self.docs_dir

        raise ValueError(f"Unknown file category: {category}")

    def save_file(self, file_obj: FileStorage) -> dict:
        """
        Validate, categorize, generate unique name,
        and save file to the appropriate folder.
        """
        if not file_obj or not file_obj.filename:
            return {"error": "Invalid file or missing filename"}

        clean_filename = secure_filename(file_obj.filename)
        ext = self.get_extension(clean_filename)

        category = self.detect_category(clean_filename)
        if not category:
            allowed = self.ALLOWED_IMAGE_EXTENSIONS | self.ALLOWED_DOCUMENT_EXTENSIONS
            msg = (
                f"Unsupported file type. Allowed formats: {', '.join(sorted(allowed))}"
            )
            return {"error": msg}

        try:
            target_dir = self.get_target_directory(category)
        except ValueError as e:
            return {"error": str(e)}

        os.makedirs(target_dir, exist_ok=True)

        unique_name = f"{uuid.uuid4().hex}.{ext}"
        destination_path = os.path.join(target_dir, unique_name)

        try:
            file_obj.save(destination_path)
            return {
                "success": True,
                "file_path": destination_path,
                "filename": unique_name,
                "original_filename": clean_filename,
                "category": category,
            }
        except Exception as e:
            if os.path.exists(destination_path):
                os.remove(destination_path)
            return {"error": f"Failed to save file: {str(e)}"}
