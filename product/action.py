"""All action can do for product"""

from db import JsonDB

from .product import Product


class Action:
    """All action can do for product"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def getaproduct(self, idproduct: str) -> dict:
        """Return a product from json file with idproduct"""
        data = self.db.load()
        for product in data["products"]:
            if product["id"] == idproduct:
                return product

    def getallproduct(self) -> dict:
        """Return all product from json file"""
        data = self.db.load()
        return data["products"]

    def addproduct(self, product: Product) -> None:
        """Add product in json file"""
        data = self.db.load()
        data["products"].append(
            {
                "id": product.id,
                "timestamp": product.timestamp,
                "portnumber": product.portnumber,
                "name": product.name,
                "total": product.total,
                "image": product.image,
            }
        )
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
                data["products"][index] = {
                    "id": newproduct.id,
                    "timestamp": newproduct.timestamp,
                    "portnumber": newproduct.portnumber,
                    "name": newproduct.name,
                    "total": newproduct.total,
                    "image": newproduct.image,
                }
        self.db.save(data)
