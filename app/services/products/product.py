"""All action can do for product"""

import os

import pandas as pd

from app.core.db import JsonDB, db_json
from app.models.product import Product

from .search import SearchAPI
from .upload_file import UploadFileAPI


class Action:
    """All action can do for product"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def search(self, query: str) -> list:
        """Search api products"""
        products = self.getallproduct()
        search_api = SearchAPI(query)
        return search_api.search_products(products)

    def get_a_product_by_id(self, idproduct: str) -> dict | None:
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

    def upload_file_image(self, idproduct, file_data, filename):
        """Upload file image"""
        upload_file_api = UploadFileAPI(self.db)
        data = upload_file_api.upload_image(idproduct, file_data, filename)
        return data

    def upload_file_docs(self, idproduct, file_data, filename):
        """Upload file docs"""
        upload_file_api = UploadFileAPI(self.db)
        data = upload_file_api.upload_docs(idproduct, file_data, filename)
        return data

    def read_product_from_excel(self, excel_file) -> None:
        """Extract data from excel and save in database"""
        excel_data = pd.read_excel(excel_file, sheet_name=None)

        for _, df in excel_data.items():
            df = df.replace({pd.NA: None, float("nan"): None})
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient="records")

            for item in records:
                product = Product(
                    description=item.get("DISCRIPTION") or "NA",
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
