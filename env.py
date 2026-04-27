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
        "DB_PRODUCT_IMAGE": os.environ.get("DB_PRODUCT_IMAGE"),
    }


envs = getenv()

db_address = envs.get("DB_ADDRESS")
db_product_image = envs.get("DB_PRODUCT_IMAGE")
