"""issuing an invoice"""

from flasgger import swag_from
from flask import Blueprint, request

from app.apis.deps import json_response
from app.core.db import db_json
from app.models.invoice import Invoice
from app.repository.invoice import InvoiceRepository
from app.repository.product import ProductRepository
from app.services.deps import idgen, timestampgen
from app.services.invoice import InvoiceService
from app.services.products.product import ProductService

invoice_bp = Blueprint("invoice", __name__)

product_repository = ProductRepository(db=db_json)
product_service = ProductService(db=db_json, repo=product_repository)

invoice_repository = InvoiceRepository(db=db_json)
invoice_service = InvoiceService(repo=invoice_repository)


def _get_product_field(product, key, default=None):
    """Helper function to read a field whether the product is an object or a dict"""
    if hasattr(product, key):
        return getattr(product, key)
    if isinstance(product, dict):
        return product.get(key, default)
    return default


@invoice_bp.route("/invoice/edit/<invoice_id>", methods=["PUT"])
@swag_from("./docs/invoice/edit_invoice.yml")
def edit_invoice(invoice_id: str):
    """Updateing invoice"""

    try:
        # finde old invoice from database
        old_invoice_data = invoice_service.get_a_invoice_by_id(invoice_id)
        if not old_invoice_data:
            return (
                json_response(
                    False,
                    f"invoice with ID '{invoice_id}' not found.",
                    errors={"id": f"invoice with ID '{invoice_id}' not found."},
                ),
                404,
            )

        # convert dict invoice to object invoice
        old_invoice = Invoice.from_dict(old_invoice_data)

        # reade body request
        body = request.get_json() or {}
        new_invoice_data = body.get("new_invoice")
        if not new_invoice_data:
            return (
                json_response(
                    False,
                    "Missing 'new_invoice' data.",
                ),
                400,
            )

        new_invoice = Invoice.from_dict(new_invoice_data)

        # increment old qty in database
        for prod in old_invoice.products:
            prod_id = _get_product_field(prod, "id") or _get_product_field(
                prod, "product_id"
            )
            prod_qty = _get_product_field(prod, "qty", 0)
            if prod_id:
                product_service.increase_qty(prod_id, prod_qty)

        # decreament new qty in database
        for prod in new_invoice.products:
            prod_id = _get_product_field(prod, "id") or _get_product_field(
                prod, "product_id"
            )
            prod_qty = _get_product_field(prod, "qty", 0)
            if prod_id:
                db_product = product_service.get_a_product_by_id(prod_id)
                if not db_product:
                    return (
                        json_response(
                            False,
                            f"Product {prod_id} not found.",
                        ),
                        404,
                    )
                if db_product.get("qty", 0) < prod_qty:
                    return (
                        json_response(
                            False,
                            f"Not enough stock for product {prod_id}.",
                        ),
                        400,
                    )
                product_service.decrease_qty(prod_id, prod_qty)

        invoice_service.edit_invoice(invoice_id, new_invoice.to_dict())

        return (
            json_response(
                True,
                "The invoice was successfuly edited",
            ),
            200,
        )
    except Exception as e:
        print(f"Error removing invoice: {e}")
        return (
            json_response(
                False,
                "Internal server error while editing invoice.",
                errors={"error": str(e)},
            ),
            500,
        )


@invoice_bp.route("/invoice/delete/<id_invoice>", methods=["DELETE"])
@swag_from("./docs/invoice/remove_a_invoice.yml")
def remove_a_invoice(id_invoice: str) -> tuple:
    """Remove a invoice in db"""
    try:
        deleted = invoice_service.get_a_invoice_by_id(id_invoice)
        if deleted:
            invoice_service.delete_a_invoice(id_invoice)
            return (
                json_response(
                    True,
                    "The invoice was successfully removed.",
                ),
                200,
            )
        return (
            json_response(
                False,
                f"invoice with ID '{id_invoice}' not found.",
                errors={"id": f"invoice with ID '{id_invoice}' not found."},
            ),
            404,
        )
    except Exception as e:
        print(f"Error removing invoice: {e}")
        return (
            json_response(
                False,
                "Internal server error while removing invoice.",
            ),
            500,
        )


@invoice_bp.route("/invoice/<id_invoice>", methods=["GET"])
@swag_from("./docs/invoice/get_a_invoice.yml")
def load_a_invoice(id_invoice: str) -> tuple:
    """Return a invoice in db"""
    invoice = invoice_service.get_a_invoice_by_id(id_invoice)
    if invoice:
        return (
            json_response(
                True,
                "Invoice received successfully.",
                data=invoice,
            ),
            200,
        )
    return (
        json_response(
            False,
            f"Invoice with ID '{id_invoice}' not found.",
            errors={"id": f"invoice with ID '{id_invoice}' not found."},
        ),
        404,
    )


@invoice_bp.route("/invoices", methods=["GET"])
@swag_from("./docs/invoice/get_all_invoice.yml")
def load_all_invoice() -> tuple:
    """Return all invoice in db"""
    invoices = invoice_service.get_all_invoice()
    return (
        json_response(
            True,
            "Invoice list successfuly received",
            data=invoices,
        ),
        200,
    )


@invoice_bp.route("/invoice", methods=["POST"])
@swag_from("./docs/invoice/get_invoice.yml")
def get_invoice() -> tuple:
    """get invoice"""

    body = request.get_json()
    selected_products = body.get("products")

    if not selected_products:
        return {"error": "No products provided"}, 400

    for item in selected_products:
        product = product_service.get_a_product_by_id(item["id"])

        if not product:
            return {"error": f"Product {item['id']} not found"}, 404

        if product["qty"] < item["qty"]:
            return {"error ": f"Not enough stock for product {item['id']}"}, 400

        product_service.decrease_qty(
            product_id=item["id"],
            amount=item["qty"],
        )

    invoices = {
        "id": str(idgen()),
        "products": selected_products,
        "timestamp": timestampgen(),
    }

    invoice_service.add_invoice(invoices)

    return (
        json_response(
            True,
            "Invoice processed successfuly",
            data=selected_products,
        ),
        200,
    )
