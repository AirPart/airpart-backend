"""Data access, relation database and all intraction with database"""

import os
from typing import List

from app.core.db import JsonDB
from app.models.product import Product


class ProductRepository:
    """Product data access repository"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def get_all(self) -> List[Product]:
        """Return all product from json file"""
        data = self.db.load()
        return data["products"]

    def get_by_id(self, product_id: str) -> Product | None:
        """Return a product from json file with product ID"""
        data = self.db.load()
        for product in data["products"]:
            if product["id"] == product_id:
                return product
        return None

    def add(self, product: Product) -> None:
        """Add product in json file with product object"""
        data = self.db.load()
        data["products"].append(product.to_dict())
        self.db.save(data)

    def delete(self, product_id) -> None:
        """Remove product from json file with product ID"""
        data = self.db.load()
        for product in data["products"]:
            if product["id"] == product_id:
                data["products"].remove(product)
                if product["image"]:
                    os.remove(product["image"])
                if product["document"]:
                    os.remove(product["document"])
        self.db.save(data)

    def update(self, product_id, new_product) -> None:
        """Edit product in json file with product ID and new product object"""
        data = self.db.load()
        for index, product in enumerate(data["products"]):
            if product["id"] == product_id:
                data["products"][index] = new_product.to_dict()
        self.db.save(data)
