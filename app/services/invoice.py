"""All action can do for invoice"""

from app.core.db import JsonDB, db_json


class Action:
    """All action can do for invoice"""

    def __init__(self, db: JsonDB) -> None:
        self.db = db

    def delete_a_invoice(self, id_invoice: str) -> None:
        """Remove inovice from db"""
        data = self.db.load()
        for invoice in data["invoices"]:
            if invoice["id"] == id_invoice:
                data["invoices"].remove(invoice)

        self.db.save(data)

    def get_a_invoice_by_id(self, id_invoice):
        """Return a invoice finded by id"""
        data = self.db.load()
        for invoice in data["invoices"]:
            if invoice["id"] == id_invoice:
                return invoice
        return None

    def get_all_invoice(self):
        """Return all invoice in db"""
        data = self.db.load()
        return data["invoices"]

    def add_invoice(self, invoice):
        """Added a invoice in db"""
        data = self.db.load()

        data["invoices"].append(invoice)

        self.db.save(data)

    def decrease_qty(self, product_id: str, amount: int):
        """decrease qty product"""
        data = self.db.load()

        for product in data["products"]:
            if product["id"] == product_id:
                product["qty"] -= amount
                break

        self.db.save(data)

    def increase_qty(self, product_id: str, amount: int):
        """decrease qty product"""
        data = self.db.load()

        for product in data["products"]:
            if product["id"] == product_id:
                product["qty"] += amount
                break

        self.db.save(data)


action_invoice = Action(db_json)
