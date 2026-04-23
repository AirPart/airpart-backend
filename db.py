"""load data in json file"""

import json
import os
import sys

from env import db_address


class JsonDB:
    """Db class"""

    def __init__(self, database_address: str):
        self.database_address = database_address

    def load(self):
        """Load data from json file"""
        if not os.path.exists(self.database_address):
            return {"products": []}
        with open(self.database_address, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        """Save data in json file"""
        with open(self.database_address, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )


if db_address is None:
    print("Error: DB_ADDRESS environment variable is not set. Exiting.")
    sys.exit(1)

db_json = JsonDB(db_address)
