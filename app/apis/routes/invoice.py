"""issuing an invoice"""

import logging

from flasgger import swag_from
from flask import Blueprint, request

from app.apis.deps import json_response
from app.core.db import db_json
from app.core.exception import (
    InsufficientStockError,
    InvoiceNotFoundError,
    ProductNotFoundError,
    ValidationError,
)
from app.models.invoice import Invoice
from app.repository.invoice import InvoiceRepository
from app.repository.product import ProductRepository
from app.services.invoice import InvoiceService
from app.services.products.product import ProductService

logger = logging.getLogger(__name__)

invoice_bp = Blueprint("invoice", __name__)

product_repository = ProductRepository(db=db_json)
product_service = ProductService(db=db_json, repo=product_repository)

invoice_repository = InvoiceRepository(db=db_json)
invoice_service = InvoiceService(repo=invoice_repository)


@invoice_bp.route("/invoice/edit/<invoice_id>", methods=["PUT"])
@swag_from("./docs/invoice/edit_invoice.yml")
def edit_invoice(invoice_id: str) -> tuple:
    """Updateing invoice endpoint"""
    body = request.get_json() or {}
    new_invoice_data = body.get("new_invoice")

    if not new_invoice_data:
        return json_response(False, "Missing 'new_invoice' data"), 400

    try:
        invoice_service.update_invoice_with_stock(
            invoice_id=invoice_id,
            new_invoice_data=new_invoice_data,
            product_service=product_service,
        )
        return json_response(True, "The invoice was succsessfuly edited"), 200
    except (InvoiceNotFoundError, ProductNotFoundError) as e:
        logger.warning("Resource not found while editing invoice %s: %s", invoice_id, e)
        return (
            json_response(
                False,
                str(e),
                errors={"error": str(e)},
            ),
            404,
        )
    except InsufficientStockError as e:
        logger.warning("Insufficient stock while editing invoice %s: %s", invoice_id, e)
        return (
            json_response(
                False,
                str(e),
                errors={"error": str(e)},
            ),
            400,
        )
    except ValidationError as e:
        logger.warning("Validation error while editing invoice %s: %s", invoice_id, e)
        return (
            json_response(
                False,
                str(e),
                errors={"error": str(e)},
            ),
            400,
        )
    except Exception as e:
        logger.error(
            "Internal server error while editing invoice: %s", e, exc_info=True
        )
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
    """Remove an invoice in db"""
    try:
        invoice_service.delete_a_invoice(id_invoice)
        return json_response(True, "The invoice was succsessfuly removed"), 200
    except InvoiceNotFoundError as e:
        return json_response(False, str(e), errors={"id": str(e)}), 404
    except Exception as e:
        logger.error("Error removing %s", e, exc_info=True)
        return (
            json_response(False, "Internal server error while removing invoice"),
            500,
        )


@invoice_bp.route("/invoice/<id_invoice>", methods=["GET"])
@swag_from("./docs/invoice/get_a_invoice.yml")
def load_a_invoice(id_invoice: str) -> tuple:
    """Return an invoice by ID"""
    invoice = invoice_service.get_a_invoice_by_id(id_invoice)
    if invoice:
        return json_response(True, "Invoice received succsessfuly", data=invoice), 200
    return (
        json_response(
            False,
            f"Invoice with ID '{id_invoice}' not found.",
            errors={"id": f"Invoice with ID '{id_invoice}' not found"},
        ),
        404,
    )


@invoice_bp.route("/invoices", methods=["GET"])
@swag_from("./docs/invoice/get_all_invoice.yml")
def load_all_invoice() -> tuple:
    """Return all invoices in db"""
    invoices_data = invoice_service.get_all_invoice()
    invoices = []
    for inv_data in invoices_data:
        try:
            invoice = (
                Invoice.from_dict(inv_data).to_dict()
                if isinstance(inv_data, dict)
                else inv_data.to_dict()
            )
            invoices.append(invoice)
        except Exception:
            invoices.append(inv_data)
    return json_response(True, "Invoice list succsessfuly received", data=invoices), 200


def _create_invoice() -> tuple:
    """Internal helper to process invoice creation"""
    body = request.get_json() or {}

    try:
        invoice = invoice_service.create_invoice_with_stock(
            invoice_data=body,
            product_service=product_service,
        )
        return (
            json_response(
                True,
                "Invoice processed successfuly",
                data=invoice.to_dict(),
            ),
            200,
        )
    except ProductNotFoundError as e:
        return json_response(False, str(e)), 404
    except (InsufficientStockError, ValidationError) as e:
        return json_response(False, str(e)), 400
    except Exception as e:
        logger.error("Error processing invoice: %s", e, exc_info=True)
        return json_response(False, f"Error processing invoice: {str(e)}"), 500


@invoice_bp.route("/invoice/add", methods=["POST"])
@swag_from("./docs/invoice/add_invoice.yml")
def create_invoice() -> tuple:
    """Create and save a new invoice."""
    return _create_invoice()


@invoice_bp.route("/invoice", methods=["POST"])
@swag_from("./docs/invoice/add_invoice_legacy.yml")
def create_invoice_legacy() -> tuple:
    """Deprecated legacy endpoint"""
    logger.warning(
        "Deprecated endpoint used %s %s. Use POST‌ /invoice/add/ instead. remote_add=%s",
        request.method,
        request.path,
        request.remote_addr,
    )
    return _create_invoice()
