"""All action can do for product"""

import os
import sys
import uuid

import pandas as pd

from db import JsonDB, db_json
from env import db_product_docs, db_product_image

from .product import Product


class Action:
    """All action can do for product"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db
        self.allowed_extensions_image = {"png", "jpg", "jpeg", "gif"}
        self.allowed_extensions_docs = {"pdf"}

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
                if product["image"]:
                    os.remove(product["image"])
                if product["document"]:
                    os.remove(product["document"])
        self.db.save(data)

    def putproduct(self, idproduct: str, newproduct: Product) -> None:
        """Edit product in json file"""
        data = self.db.load()
        for index, product in enumerate(data["products"]):
            if product["id"] == idproduct:
                data["products"][index] = newproduct.to_dict()
        self.db.save(data)

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

    def read_product_from_excel(self, excel_file) -> None:
        """Extract data from excel and save in database"""
        excel_data = pd.read_excel(excel_file, sheet_name=None)

        for _, df in excel_data.items():
            df = df.replace({pd.NA: None, float("nan"): None})
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient="records")

            for item in records:
                product = Product(
                    discription=item.get("DISCRIPTION") or "NA",
                    part_number=item.get("PART NO.") or "NA",
                    serial_number=item.get("SERIAL NO.") or "NA",
                    qty=item.get("QTY") or "NA",
                    unit=item.get("UNIT") or "NA",
                    price=float(item.get("PRICE") or 0.0),
                    alternate=item.get("ALTERNATE") or "NA",
                    company=item.get("COMPANY") or "NA",
                )
                self.addproduct(product)


action_product = Action(db_json)
