"""All action can do for product"""

import os
import sys
import uuid

from db import JsonDB, db_json
from env import db_product_image

from .product import Product


class Action:
    """All action can do for product"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db
        self.allowed_extensions = {"png", "jpg", "jpeg", "gif"}

    def getaproduct(self, idproduct: str) -> dict | None:
        """Return a product from json file with idproduct"""
        data = self.db.load()
        for product in data["products"]:
            if product["id"] == idproduct:
                return product
        return None

    def getallproduct(self) -> list:
        """Return all product from json file"""
        data = self.db.load()
        return data["products"]

    def addproduct(self, product: Product) -> None:
        """Add product in json file"""
        data = self.db.load()
        data["products"].append(product.to_dict())
        self.db.save(data)

    def rmproduct(self, idproduct: str) -> None:
        """Remove projuct from json file"""
        data = self.db.load()
        for product in data["products"]:
            if product["id"] == idproduct:
                data["products"].remove(product)
        self.db.save(data)

    def putproduct(self, idproduct: str, newproduct: Product) -> None:
        """Edit product in json file"""
        data = self.db.load()
        for index, product in enumerate(data["products"]):
            if product["id"] == idproduct:
                data["products"][index] = newproduct.to_dict()
        self.db.save(data)

    def allowed_file(self, filename):
        """Check allowed extensions file"""
        return (
            "." in filename
            and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions
        )

    def generate_unique_filename(self, filename):
        """Generate unique filename with uuid"""
        ext = filename.rsplit(".", 1)[1].lower()
        unique_id = str(uuid.uuid4())
        return f"{unique_id}.{ext}"

    def upload_image(self, id_product: str, file_data, filename: str) -> dict | None:
        """Upload product image in server"""

        if db_product_image is None:
            print("Error: DB_PRODUCT_IMAGE environment variable is not set. Exiting.")
            sys.exit(1)

        if not os.path.exists(db_product_image):
            os.mkdir(db_product_image)

        if not filename or not self.allowed_file(filename):
            return {"error": "Invalid file or file type not allowed"}

        unique_filename = self.generate_unique_filename(filename)
        filepath = os.path.join(db_product_image, unique_filename)

        try:
            with open(filepath, "wb") as f:
                f.write(file_data)
                # f.write(file_data.read())

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


action_product = Action(db_json)
