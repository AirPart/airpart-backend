"""All action can do for invoice"""

from db import JsonDB, db_json


class Action:
    """All action can do for invoice"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def add_invoice(self, invoice):
        """Added a invoice in db"""
        data = self.db.load()

        data["invoice"].append(invoice)

        self.db.save(data)

    def decrease_qty(self, product_id: str, amount: int):
        """decrease qty product"""
        data = self.db.load()

        for product in data["products"]:
            if product["id"] == product_id:
                product["qty"] -= amount
                break

        self.db.save(data)


action_invoice = Action(db_json)
