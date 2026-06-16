"""Validation, workflow and Bussines logic product"""

from typing import List

import pandas as pd

from app.core.db import JsonDB
from app.models.product import Product
from app.repository.product import ProductRepository

from .search import SearchAPI
from .upload_file import UploadFileAPI


class ProductService:
    """Bussines logic, validation and wrokfolw product service"""

    def __init__(self, db: JsonDB, repo: ProductRepository) -> None:
        self.repo = repo
        self.db = db

    def search(self, query: str) -> list:
        """Search api products"""
        products = self.repo.get_all()
        search_api = SearchAPI(query)
        return search_api.search_products(products)

    def get_a_product_by_id(self, idproduct: str) -> Product | None:
        """Get a product workflow, validation and Bussines logic"""
        return self.repo.get_by_id(product_id=idproduct)

    def getallproduct(self) -> List[Product]:
        """Get all product workflow, validation and Bussines logic"""
        return self.repo.get_all()

    def addproduct(self, product: Product) -> None:
        """Add a product workflow, validation and Bussines logic"""
        self.repo.add(product=product)

    def rmproduct(self, idproduct: str) -> None:
        """Remove projuct workflow, validation and Bussines logic"""
        self.repo.delete(product_id=idproduct)

    def putproduct(self, idproduct: str, newproduct: Product) -> None:
        """Edit product workflow, validation and Bussines logic"""
        self.repo.update(product_id=idproduct, new_product=newproduct)

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
                self.repo.add(product)
