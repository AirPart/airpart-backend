"""issuing an invoice"""

from flasgger import swag_from
from flask import Blueprint, request

from app.apis.deps import json_response
from app.core.db import db_json
from app.repository.product import ProductRepository
from app.services.deps import idgen, timestampgen
from app.services.invoice import action_invoice
from app.services.products.product import ProductService

invoice_bp = Blueprint("invoice", __name__)

product_repository = ProductRepository(db=db_json)
product_service = ProductService(db=db_json, repo=product_repository)


@invoice_bp.route("/invoice/edit/<invoice_id>", methods=["PUT"])
@swag_from("./docs/invoice/edit_invoice.yml")
def edit_invoice(invoice_id: str):
    """Updateing invoice"""

    try:
        # finde old invoice from database
        invoice = action_invoice.get_a_invoice_by_id(invoice_id)
        print(invoice)
        if not invoice:
            return (
                json_response(
                    False,
                    f"invoice with ID '{invoice_id}' not found.",
                    errors={"id": f"invoice with ID '{invoice_id}' not found."},
                ),
                404,
            )

        # reade body request
        body = request.get_json()
        new_invoice = body.get("new_invoice")
        print(new_invoice)

        # increment old qty in database
        for old_invoice in invoice["products"]:
            action_invoice.increase_qty(
                old_invoice["id"],
                old_invoice["qty"],
            )

        # decreament new qty in database
        for new_item in new_invoice["products"]:
            action_invoice.decrease_qty(
                new_item["id"],
                new_item["qty"],
            )

        # update invoice with new invoice
        invoice["id"] = new_invoice["id"]
        invoice["products"] = new_invoice["products"]
        invoice["timestamp"] = new_invoice["timestamp"]

        # invoice["invoice_id"] = new_invoice["invoice_id"]
        # invoice["products"] = new_invoice["products"]
        # invoice["custormer"] = new_invoice["coustomer"]
        # invoice["seller"] = new_invoice["seller"]
        # invoice["bill_to"] = new_invoice["bill_to"]
        # invoice["ship_to"] = new_invoice["ship_to"]
        # invoice["terms"] = new_invoice["terms"]
        # invoice["subtotal"] = new_invoice["subtotal"]
        # invoice["descount"] = new_invoice["descount"]
        # invoice["shipping"] = new_invoice["shipping"]
        # invoice["seles_tax"] = new_invoice["seles_tax"]
        # invoice["total"] = new_invoice["total"]
        # invoice["due_date"] = new_invoice["due_date"]
        # invoice["invoice_doc"] = new_invoice["invoice_doc"]
        # invoice["timestamp"] = new_invoice["timestamp"]

        # added new invoice in database
        action_invoice.edit_invoice(invoice_id, invoice)

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
                errors={"error": e},
            ),
            500,
        )


@invoice_bp.route("/invoice/delete/<id_invoice>", methods=["DELETE"])
@swag_from("./docs/invoice/remove_a_invoice.yml")
def remove_a_invoice(id_invoice: str) -> tuple:
    """Remove a invoice in db"""
    try:
        deleted = action_invoice.get_a_invoice_by_id(id_invoice)
        if deleted:
            action_invoice.delete_a_invoice(id_invoice)
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
@swag_from("./docs/invoice/get_all_invoice.yml")
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

    return (
        json_response(
            True,
            "Invoice processed successfuly",
            data=selected_products,
        ),
        200,
    )
