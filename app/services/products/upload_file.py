"""Upload file api"""

import os
import sys
import uuid

from app.core.config import db_product_docs, db_product_image


class UploadFileAPI:
    """Upload file api"""

    def __init__(self, db) -> None:

        self.db = db
        self.allowed_extensions_image = {"png", "jpg", "jpeg", "gif"}
        self.allowed_extensions_docs = {"pdf"}

    def allowed_file_image(self, filename):
        """Check allowed extensions file"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions_image
        )

    def allowed_file_docs(self, filename):
        """Check allowed extensions file"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions_docs
        )

    def generate_unique_filename(self, filename):
        """Generate unique filename with uuid"""
        ext = filename.rsplit(".", 1)[1].lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{ext}"

    def upload_docs(self, id_product: str, file_data, filename: str) -> dict | None:
        """Upload product docs in server"""

        if db_product_docs is None:
            print("Error: DB_PRODUCT_DOCS environment variable is not set. Exiting.")
            sys.exit(1)

        if not os.path.exists(db_product_docs):
            os.mkdir(db_product_docs)

        if not filename or not self.allowed_file_docs(filename):
            return {"error": "Invalid file or file type not allowed"}

        unique_filename = self.generate_unique_filename(filename)
        filepath = os.path.join(db_product_docs, unique_filename)

        try:
            with open(filepath, "wb") as f:
                f.write(file_data.read())

            data = self.db.load()
            product_updated = False
            for product in data["products"]:
                if product.get("id") == id_product:
                    product["document"] = filepath
                    product_updated = True

            if product_updated:
                self.db.save(data)
                return {
                    "message": "document uploaded successfuly",
                    "document_url": filepath,
                }
            if os.path.exists(filepath):
                os.remove(filepath)
                return {"error": f"Product with id {id_product} not found."}

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {"error": f"Failed to process upload: {str(e)}"}

    def upload_image(self, id_product: str, file_data, filename: str) -> dict | None:
        """Upload product image in server"""

        if db_product_image is None:
            print("Error: DB_PRODUCT_IMAGE environment variable is not set. Exiting.")
            sys.exit(1)

        if not os.path.exists(db_product_image):
            os.mkdir(db_product_image)

        if not filename or not self.allowed_file_image(filename):
            return {"error": "Invalid file or file type not allowed"}

        unique_filename = self.generate_unique_filename(filename)
        filepath = os.path.join(db_product_image, unique_filename)

        try:
            with open(filepath, "wb") as f:
                f.write(file_data.read())
                # f.write(file_data)

            data = self.db.load()
            product_updated = False
            for product in data["products"]:
                if product.get("id") == id_product:
                    product["image"] = filepath
                    product_updated = True

            if product_updated:
                self.db.save(data)
                return {"message": "Image uploaded successfuly", "image_url": filepath}
            if os.path.exists(filepath):
                os.remove(filepath)
                return {"error": f"Product with id {id_product} not found."}

        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return {"error": f"Failed to process upload: {str(e)}"}
