"""Run app space"""

from db import JsonDB
from env import getenv


def main():
    """Main app"""
    envs = getenv()
    db = JsonDB(envs.get("DB_ADDRESS"))
    data = db.load()
    data["products"].append(
        {
            "portnumber": "94ho84h",
            "name": "bolt",
            "total": 45,
        }
    )
    db.save(data)


if __name__ == "__main__":
    main()
