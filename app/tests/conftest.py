import pytest
from flask import Flask

from app.apis.routes.files import file_bp
from app.apis.routes.invoice import invoice_bp
from app.apis.routes.product import product_bp


@pytest.fixture
def app():
    """Create Flask application test instance with registered blueprints"""
    app = Flask(__name__)
    app.register_blueprint(invoice_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(file_bp)

    app.config["TESTING"] = True
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


@pytest.fixture
def mock_product_data():
    return {
        "id": "prod-1",
        "description": "Test Product",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": 10,
        "unit": "PCS",
        "price": 100.0,
        "alternate": "ALT-001",
        "company": "Test Company",
        "document": None,
        "image": None,
        "timestamp": None,
    }
