"""Apis products for managing for product action"""

from flask import Blueprint, request

from product import Product
from product.action import action_product
from utils import json_response

product_bp = Blueprint("product", __name__)


@product_bp.route("/products", methods=["GET"])
def get_all_products() -> tuple:
    """Load all products from database"""
    try:
        product_list_dict = action_product.getallproduct()
        return (
            json_response(
                True,
                "Product list successfully received.",
                data=product_list_dict,
            ),
            200,
        )
    except Exception as e:
        print(f"Unexpected Errro fetching all producnts: {e}")
        return (
            json_response(
                False,
                "Internal server error while retrieving product list.",
            ),
            500,
        )


@product_bp.route("/product/<id_product>", methods=["GET"])
def get_a_product(id_product: str) -> tuple:
    """Load detail a product from database"""
    try:
        product = action_product.getaproduct(id_product)
        if product:
            return (
                json_response(
                    True,
                    "Product received successfully.",
                    data=product,
                ),
                200,
            )
        return (
            json_response(
                False,
                f"Product with ID '{id_product}' not found.",
                errors={"id": f"Product with ID '{id_product}' not found."},
            ),
            404,
        )
    except Exception as e:
        print(f"Error getting product: {e}")
        return (
            json_response(
                False,
                "Internal server error while getting product.",
            ),
            500,
        )


@product_bp.route("/product/add", methods=["POST"])
def productadd() -> tuple:
    """Add a product in database"""
    data = request.get_json()

    description = data.get("description")
    part_number = data.get("part_number")
    serial_number = data.get("serial_number")
    qty = data.get("qty")
    unit = data.get("unit")
    price = data.get("price")
    alternate = data.get("alternate")
    company = data.get("company")
    id_product = data.get("id")
    document = data.get("document")
    image = data.get("image")
    timestamp = data.get("timestamp")

    try:
        product = Product(
            description=description,
            part_number=part_number,
            serial_number=serial_number,
            unit=unit,
            price=price,
            qty=qty,
            alternate=alternate,
            company=company,
            id=id_product,
            document=document,
            image=image,
            timestamp=timestamp,
        )
        action_product.addproduct(product)
        return (
            json_response(True, "Product added successfully.", data=product.to_dict()),
            201,
        )
    except Exception as e:
        print(f"Error adding product: {e}")
        return (
            json_response(
                False,
                "Internal server error while adding product.",
            ),
            500,
        )


@product_bp.route("/product/delete/<id_product>", methods=["DELETE"])
def removeproduct(id_product: str) -> tuple:
    """Delete a product from database"""
    try:
        deleted = action_product.getaproduct(id_product)
        if deleted:
            action_product.rmproduct(id_product)
            return (
                json_response(
                    True,
                    "The product was successfully removed.",
                ),
                200,
            )
        return (
            json_response(
                False,
                f"Product with ID '{id_product}' not found.",
                errors={"id": f"Product with ID '{id_product}' not found."},
            ),
            404,
        )
    except Exception as e:
        print(f"Error removing product: {e}")
        return (
            json_response(
                False,
                "Internal server error while removing product.",
            ),
            500,
        )


@product_bp.route("/product/edit/<id_product>", methods=["PUT"])
def editproduct(id_product: str) -> tuple:
    """Edit a product in database with id"""
    data = request.get_json()

    product = action_product.getaproduct(id_product)
    if not product:
        return (
            json_response(
                False,
                f"Product with ID '{id_product}' not found.",
                errors={
                    "id": f"Product with ID '{id_product}' not found.",
                },
            ),
            404,
        )

    try:
        if data.get("description") is not None:
            product["description"] = data.get("description")
        if data.get("part_number") is not None:
            product["part_number"] = data.get("part_number")
        if data.get("serial_number") is not None:
            product["serial_number"] = data.get("serial_number")
        if data.get("qty") is not None:
            product["qty"] = data.get("qty")
        if data.get("unit") is not None:
            product["unit"] = data.get("unit")
        if data.get("price") is not None:
            product["price"] = data.get("price")
        if data.get("alternate") is not None:
            product["alternate"] = data.get("alternate")
        if data.get("company") is not None:
            product["company"] = data.get("company")
        if data.get("document") is not None:
            product["document"] = data.get("document")
        if data.get("image") is not None:
            product["image"] = data.get("image")
        if data.get("timestamp") is not None:
            product["timestamp"] = data.get("timestamp")

        newproduct = Product(
            description=product["description"],
            part_number=product["part_number"],
            serial_number=product["serial_number"],
            unit=product["unit"],
            price=product["price"],
            qty=product["qty"],
            alternate=product["alternate"],
            company=product["company"],
            id=product["id"],
            document=product["document"],
            image=product["image"],
            timestamp=product["timestamp"],
        )

        action_product.putproduct(id_product, newproduct)
        return (
            json_response(
                True,
                "The product was successfully updated.",
                data=newproduct.to_dict(),
            ),
            200,
        )
    except Exception as e:
        print(f"Error editing product: {e}")
        return (
            json_response(
                False,
                "Internal server error while editing product.",
            ),
            500,
        )
