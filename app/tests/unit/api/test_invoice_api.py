"""Tests for Invoice API Routes"""

from unittest.mock import Mock, patch

from app.core.exception import InsufficientStockError, InvoiceNotFoundError

# ==============================================================================
# GET /invoices
# ==============================================================================


@patch("app.apis.routes.invoice.invoice_service")
def test_load_all_invoice(mock_inv_service, client, mock_invoice_data):
    """Test retrieving list of all invoices"""
    mock_inv_service.get_all_invoice.return_value = [mock_invoice_data]

    response = client.get("/invoices")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert len(json_data["data"]) == 1
    assert json_data["data"][0]["id"] == "test-invoice-123"


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
# POST /invoice
# ==============================================================================


@patch("app.apis.routes.invoice.invoice_service")
def test_create_invoice_success(mock_inv_service, client):
    """Test successful creation of invoice when stock is sufficient"""
    mock_invoice = Mock()
    mock_invoice.to_dict.return_value = {
        "id": "test-invoice-123",
        "customer": "John Doe",
        "total": 104.0,
    }
    mock_inv_service.create_invoice_with_stock.return_value = mock_invoice

    payload = {
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
        "products": [
            {
                "id": "prod-1",
                "description": "Keyboard",
                "part_number": "KB-001",
                "serial_number": "SN-001",
                "unit": "pcs",
                "alternate": "Alt Keyboard",
                "company": "Acme Corp",
                "qty": 2,
                "price": 100.0,
            }
        ],
    }

    response = client.post("/invoice", json=payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    assert json_data["data"]["customer"] == "John Doe"
    mock_inv_service.create_invoice_with_stock.assert_called_once()


@patch("app.apis.routes.invoice.invoice_service")
def test_create_invoice_out_of_stock(mock_inv_service, client):
    """Test creation fails with 400 when product quantity exceeds available stock"""
    mock_inv_service.create_invoice_with_stock.side_effect = InsufficientStockError(
        "prod-1", 2, 5
    )

    payload = {
        "products": [
            {
                "id": "prod-1",
                "description": "Keyboard",
                "part_number": "KB-001",
                "serial_number": "SN-001",
                "unit": "pcs",
                "alternate": "Alt Keyboard",
                "company": "Acme Corp",
                "qty": 5,
                "price": 100.0,
            }
        ]
    }

    response = client.post("/invoice", json=payload)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["success"] is False


# ==============================================================================
# DELETE /invoice/delete/<id>
# ==============================================================================


@patch("app.apis.routes.invoice.invoice_service")
def test_remove_a_invoice_success(mock_inv_service, client):
    """Test successfully removing an invoice"""
    mock_inv_service.delete_a_invoice.return_value = True

    response = client.delete("/invoice/delete/test-invoice-123")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    mock_inv_service.delete_a_invoice.assert_called_once_with("test-invoice-123")


@patch("app.apis.routes.invoice.invoice_service")
def test_remove_a_invoice_not_found(mock_inv_service, client):
    """Test deleting non-existent invoice returns 404"""
    mock_inv_service.delete_a_invoice.side_effect = InvoiceNotFoundError(
        "Invoice unknown-id not found"
    )

    response = client.delete("/invoice/delete/unknown-id")
    assert response.status_code == 404
    json_data = response.get_json()
    assert json_data["success"] is False


# ==============================================================================
# PUT /invoice/edit/<id>
# ==============================================================================


@patch("app.apis.routes.invoice.invoice_service")
def test_edit_invoice_success(mock_inv_service, client):
    """Test editing an existing invoice correctly delegates to service"""
    mock_updated_invoice = Mock()
    mock_updated_invoice.to_dict.return_value = {
        "id": "test-invoice-123",
        "customer": "Updated Doe",
        "total": 300.0,
    }
    mock_inv_service.update_invoice_with_stock.return_value = mock_updated_invoice

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
            {"id": "prod-1", "description": "Keyboard", "qty": 3, "price": 100}
        ],
    }

    payload = {"new_invoice": new_invoice}

    response = client.put("/invoice/edit/test-invoice-123", json=payload)

    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["success"] is True
    mock_inv_service.update_invoice_with_stock.assert_called_once()
