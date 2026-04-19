"""Run app space"""

from db import JsonDB
from env import getenv
from product import Action, Product


def main():
    """Main app"""
    product = Product(portnumber="8js374", name="bolt", total=45)

    envs = getenv()
    db = JsonDB(envs.get("DB_ADDRESS"))
    action = Action(db)
    action.addproduct(product)
    # action.rmproduct("722033d3-30bb-41b6-95b9-8f41c09fe43a")
    # action.putproduct(
    #     "aa040f6a-3c10-4b29-92dd-2cc423bb7b94",
    #     {
    #         "portnumbr": "49j88h",
    #         "name": "bolt",
    #         "total": 20,
    #     },
    # )
    # products = action.getallproduct()
    # print(products)
    # product = action.getaproduct("26ef6711-7511-4b81-a43e-6285cf34ee3c")
    # print(product)


if __name__ == "__main__":
    main()
