"""load data in json file"""

import json
import os


class JsonDB:
    """Db class"""

    def __init__(self, db_address: str):
        self.db_address = db_address

    def load(self):
        """Load data from json file"""
        if not os.path.exists(self.db_address):
            return {
                "products": [],
            }
        with open(self.db_address, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        """Save data in json file"""
        with open(self.db_address, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )
