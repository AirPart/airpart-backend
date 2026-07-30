"""Tests for Invoice API Routes"""

from unittest.mock import patch

import pytest
from flask import Flask

from app.apis.routes.invoice import invoice_bp


@pytest.fixture
def app():
    """Create Flask application test instance"""
    app = Flask(__name__)
    app.register_blueprint(invoice_bp)
    return app


@pytest.fixture
def client(app):
    """Create Flask test client"""
    return app.test_client()


@pytest.fixture
def mock_invoice_data():
    """Fixture containing a mock invoice dict matching the schema"""
    return {
        "id": "test-invoice-123",
        "invoice_id": "test-invoice-123",
        "timestamp": "2026-07-30T10:00:00",
        "customer": "John Doe",
        "seller": "Acme Corp",
        "bill_to": "John's Office",
        "ship_to": "John's Home",
        "terms": "Net 30",
        "subtotal": 100.0,
        "descount": 10.0,
        "shipping": 5.0,
        "seles_tax": 9.0,
        "total": 104.0,
        "due_date": "2026-08-30T10:00:00",
        "products": [{"id": "prod-1", "name": "Laptop", "qty": 1, "price": 100.0}],
    }


# ==============================================================================
# GET /invoice/<id>
# ==============================================================================


@patch("app.apis.routes.invoice.invoice_service")
def test_load_a_invoice_success(mock_inv_service, client, mock_invoice_data):
    """Test successfully loading an invoice by ID"""
    mock_inv_service.get_a_invoice_by_id.return_value = mock_invoice_data

    response = client.get("/invoice/test-invoice-123")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["id"] == "test-invoice-123"


@patch("app.apis.routes.invoice.invoice_service")
def test_load_a_invoice_not_found(mock_inv_service, client):
    """Test loading a non-existent invoice ID returns 404"""
    mock_inv_service.get_a_invoice_by_id.return_value = None

    response = client.get("/invoice/unknown-id")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["success"] is False


# ==============================================================================
# DELETE /invoice/delete/<id>
# ==============================================================================


@patch("app.apis.routes.invoice.invoice_service")
def test_remove_a_invoice_success(mock_inv_service, client, mock_invoice_data):
    """Test successfully removing an invoice"""
    mock_inv_service.get_a_invoice_by_id.return_value = mock_invoice_data
    mock_inv_service.delete_a_invoice.return_value = True

    response = client.delete("/invoice/delete/test-invoice-123")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    mock_inv_service.delete_a_invoice.assert_called_once_with("test-invoice-123")


@patch("app.apis.routes.invoice.invoice_service")
def test_remove_a_invoice_not_found(mock_inv_service, client):
    """Test deleting non-existent invoice returns 404"""
    mock_inv_service.get_a_invoice_by_id.return_value = None

    response = client.delete("/invoice/delete/unknown-id")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["success"] is False


# ==============================================================================
# PUT /invoice/edit/<id>
# ==============================================================================
@patch("app.apis.routes.invoice.product_service")
@patch("app.apis.routes.invoice.invoice_service")
def test_edit_invoice_success(
    mock_inv_service, mock_prod_service, client, mock_invoice_data
):
    """Test editing an existing invoice correctly updates stocks and updates database"""

    new_invoice = {
        "id": "test-invoice-123",
        "invoice_id": "test-invoice-123",
        "timestamp": "2026-07-30T10:00:00",
        "customer": "Updated Doe",
        "seller": "Test Seller",
        "bill_to": "Updated Doe",
        "ship_to": "Updated Doe",
        "terms": "cash",
        "subtotal": 300,
        "descount": 0,
        "shipping": 0,
        "seles_tax": 0,
        "total": 300,
        "due_date": "2026-07-30T10:00:00",
        "products": [
            {
                "id": "prod-1",
                "description": "Keyboard",
                "qty": 3,
                "price": 100,
            }
        ],
    }

    mock_inv_service.get_a_invoice_by_id.return_value = mock_invoice_data
    mock_prod_service.get_a_product_by_id.return_value = {
        "id": "prod-1",
        "qty": 10,
        "description": "Keyboard",
        "price": 100,
    }
    mock_prod_service.increase_qty.return_value = True
    mock_prod_service.decrease_qty.return_value = True
    mock_inv_service.edit_invoice.return_value = True

    payload = {"new_invoice": new_invoice}

    response = client.put("/invoice/edit/test-invoice-123", json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True

    mock_prod_service.increase_qty.assert_called_with("prod-1", 1)
    mock_prod_service.decrease_qty.assert_called_with("prod-1", 3)
