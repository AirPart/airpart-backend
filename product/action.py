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
                "description": product.description,
                "part_number": product.part_number,
                "serial_number": product.serial_number,
                "qty": product.qty,
                "unit": product.unit,
                "price": product.price,
                "alternate": product.alternate,
                "company": product.company,
                "id": product.id,
                "document": product.document,
                "image": product.image,
                "timestamp": product.timestamp,
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
                    "description": newproduct.description,
                    "part_number": newproduct.part_number,
                    "serial_number": newproduct.serial_number,
                    "qty": newproduct.qty,
                    "unit": newproduct.unit,
                    "price": newproduct.price,
                    "alternate": newproduct.alternate,
                    "company": newproduct.company,
                    "id": newproduct.id,
                    "document": newproduct.document,
                    "image": newproduct.image,
                    "timestamp": newproduct.timestamp,
                }
        self.db.save(data)
