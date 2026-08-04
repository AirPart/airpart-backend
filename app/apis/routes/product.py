"""Apis products for managing for product action"""

import os

from flasgger import swag_from
from flask import Blueprint, request
from werkzeug.utils import secure_filename

from app.apis.deps import json_response
from app.core.db import db_json
from app.models.product import Product
from app.repository.product import ProductRepository
from app.services.products.product import ProductService

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

ADD_FROM_EXCEL_YAML = os.path.join(DIR_PATH, "docs", "products", "add_from_excel.yml")
UPLOAD_IMAGE_YAML = os.path.join(DIR_PATH, "docs", "products", "upload_image.yml")
UPLOAD_DOCS_YAML = os.path.join(DIR_PATH, "docs", "products", "upload_docs.yml")

product_bp = Blueprint("product", __name__)

product_repository = ProductRepository(db=db_json)
product_service = ProductService(db=db_json, repo=product_repository)


@product_bp.route("/product/search", methods=["POST"])
@swag_from("./docs/products/search_product.yml")
def search_product() -> tuple:
    """Search products"""
    data = request.get_json()
    query = data.get("query")

    if not isinstance(query, str) or not query.strip():
        return (
            json_response(
                False,
                "query is required and must be a non-empty string",
            ),
            400,
        )

    product_search = product_service.search(query)

    return (
        json_response(
            True,
            "search products successfully",
            data=product_search,
        ),
        200,
    )


@product_bp.route("/product/<id_product>/upload_docs", methods=["POST"])
@swag_from(UPLOAD_DOCS_YAML)
def upload_docs(id_product: str) -> tuple:
    """Upload product document"""
    if "document" not in request.files:
        return (
            json_response(
                False,
                "No document file provided",
                errors={
                    "document": "File is required",
                },
            ),
            400,
        )

    document = request.files["document"]

    if document.filename == "":
        return (
            json_response(
                False,
                "Empty file.",
                errors={
                    "document": "Invalid file name",
                },
            ),
            400,
        )

    document_name = secure_filename(document.filename)
    result = product_service.upload_file_docs(id_product, document, document_name)

    if not isinstance(result, dict):
        return (
            json_response(
                False,
                "Internal backend error",
            ),
            500,
        )
    message = result.get("message")
    error = result.get("error")

    status = 200 if error is None else 400

    return (
        json_response(
            error is None,
            message=message,
            errors=error,
        ),
        status,
    )


@product_bp.route("/product/<id_product>/upload_image", methods=["POST"])
@swag_from(UPLOAD_IMAGE_YAML)
def upload_image(id_product: str) -> tuple:
    """Upload product image"""
    if "image" not in request.files:
        return (
            json_response(
                False,
                "No image file provided",
                errors={
                    "image": "File is required",
                },
            ),
            400,
        )

    image = request.files["image"]

    if image.filename == "":
        return (
            json_response(
                False,
                "Empty file.",
                errors={
                    "image": "Invalid file name",
                },
            ),
            400,
        )

    image_name = secure_filename(image.filename)
    result = product_service.upload_file_image(id_product, image, image_name)

    if not isinstance(result, dict):
        return (
            json_response(
                False,
                "Internal backend error",
            ),
            500,
        )
    message = result.get("message")
    error = result.get("error")

    status = 200 if error is None else 400

    return (
        json_response(
            error is None,
            message=message,
            errors=error,
        ),
        status,
    )


@product_bp.route("/products", methods=["GET"])
@swag_from("./docs/products/get_all_products.yml")
def get_all_products() -> tuple:
    """Load all products from database"""
    try:
        product_list_dict = product_service.getallproduct()
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
@swag_from("./docs/products/get_a_product.yml")
def get_a_product(id_product: str) -> tuple:
    """Load detail a product from database"""
    try:
        product = product_service.get_a_product_by_id(id_product)
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


DIR_PATH = os.path.dirname(os.path.realpath(__file__))

ADD_FROM_EXCEL_YAML = os.path.join(DIR_PATH, "docs", "products", "add_from_excel.yml")


@product_bp.route("/product/add_from_excel", methods=["POST"])
@swag_from(ADD_FROM_EXCEL_YAML)
def productadd_from_excel():
    """Add product from excel file"""
    if "excel_file" not in request.files:
        return (
            json_response(
                False,
                "No excel file provided",
                errors={
                    "excel_file": "File is required",
                },
            ),
            400,
        )
    excel_file = request.files["excel_file"]

    if excel_file.filename == "":
        return (
            json_response(
                False,
                "Empty file.",
                errors={
                    "excel_file": "Invalid file name",
                },
            ),
            400,
        )

    product_service.read_product_from_excel(excel_file)
    return (
        json_response(
            True,
            "Extract excel file successfully",
        ),
        200,
    )


@product_bp.route("/product/add", methods=["POST"])
@swag_from("./docs/products/add_product.yml")
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
        product_service.addproduct(product)
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
        deleted = product_service.get_a_product_by_id(id_product)
        if deleted:
            product_service.rmproduct(id_product)
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

    product = product_service.get_a_product_by_id(id_product)
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

        product_service.putproduct(id_product, newproduct)
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
