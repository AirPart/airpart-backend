"""issuing an invoice"""

from flasgger import swag_from
from flask import Blueprint, request

from invoice.action import action_invoice
from product.action import action_product
from utils import idgen, json_response, timestampgen

invoice_bp = Blueprint("invoice", __name__)


@invoice_bp.route("/invoice/<id_invoice>", methods=["GET"])
@swag_from("../docs/invoice/get_a_invoice.yml")
def load_a_invoice(id_invoice: str) -> tuple:
    """Return a invoice in db"""
    invoice = action_invoice.get_a_invoice_by_id(id_invoice)
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
@swag_from("../docs/invoice/get_all_invoice.yml")
def load_all_invoice() -> tuple:
    """Return all invoice in db"""
    invoices = action_invoice.get_all_invoice()
    return (
        json_response(
            True,
            "Invoice list successfuly received",
            data=invoices,
        ),
        200,
    )


@invoice_bp.route("/invoice", methods=["POST"])
@swag_from("../docs/invoice/get_invoice.yml")
def get_invoice() -> tuple:
    """get invoice"""

    body = request.get_json()
    selected_products = body.get("products")

    if not selected_products:
        return {"error": "No products provided"}, 400

    for item in selected_products:
        product = action_product.getaproduct(item["id"])

        if not product:
            return {"error": f"Product {item['id']} not found"}, 404

        if product["qty"] < item["qty"]:
            return {"error ": f"Not enough stock for product {item['id']}"}, 400

        action_invoice.decrease_qty(
            product_id=item["id"],
            amount=item["qty"],
        )

        invoices = {
            "id": str(idgen()),
            "products": selected_products,
            "timestamp": timestampgen(),
        }

        action_invoice.add_invoice(invoices)

    return {
        "message": "Invoice processed successfuly",
        "data": selected_products,
    }, 200
