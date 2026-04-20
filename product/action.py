"""All action can do for product"""

from db import JsonDB
from utils import idgen

from .product import Product


class Action:
    """All action can do for product"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def getaproduct(self, idproduct: str) -> dict:
        """Return a product from json file with idproduct"""
        data = self.db.load()
        for key, value in data.items():
            if key == idproduct:
                return value

    def getallproduct(self) -> dict:
        """Return all product from json file"""
        data = self.db.load()
        return data

    def addproduct(self, product: Product) -> None:
        """Add product in json file"""
        data = self.db.load()
        data[str(idgen())] = {
            "timestamp": product.timestamp,
            "portnumber": product.portnumber,
            "name": product.name,
            "total": product.total,
            "image": product.image,
        }
        self.db.save(data)

    def rmproduct(self, idproduct: str) -> None:
        """Remove projuct from json file"""
        data = self.db.load()
        del data[idproduct]
        self.db.save(data)

    def putproduct(self, idproduct: str, newproduct: Product) -> None:
        """Edit product in json file"""
        data = self.db.load()
        for key, _ in data.items():
            if key == idproduct:
                data[key] = {
                    "timestamp": newproduct.timestamp,
                    "portnumber": newproduct.portnumber,
                    "name": newproduct.name,
                    "total": newproduct.total,
                    "image": newproduct.image,
                }
        self.db.save(data)
