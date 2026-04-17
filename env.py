"""Setup variable enviroment"""

import os

from dotenv import load_dotenv


def getenv():
    """Load variable enviroment in app"""
    mode = os.environ.get("MODE", "test")
    if mode == "test":
        load_dotenv(".test.env")
    elif mode == "product":
        load_dotenv(".env")
    return {
        "DB_ADDRESS": os.environ.get("DB_ADDRESS"),
    }
