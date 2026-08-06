"""Integration tests for invoice HTTP routes."""

from unittest.mock import Mock, call

import pytest

import app.apis.routes.invoice as invoice_routes


def make_product_dict(product_id="prod-1", qty=10):
    return {
        "id": product_id,
        "timestamp": "2026-08-01T09:00:00",
        "description": "Engine Part",
        "part_number": "PN-001",
        "serial_number": "SN-001",
        "qty": qty,
        "unit": "PCS",
        "price": 100.0,
        "alternate": "ALT-001",
        "company": "AirPart",
        "document": None,
        "image": None,
    }


def make_invoice_dict(
    invoice_id="inv-1",
    products=None,
    customer="Customer A",
    total=100.0,
):
    return {
        "id": invoice_id,
        "invoice_id": invoice_id,
        "timestamp": "2026-08-01T10:00:00",
        "products": products if products is not None else [],
        "customer": customer,
        "seller": "AirPart",
        "bill_to": "Customer Office",
        "ship_to": "Customer Warehouse",
        "terms": "Net 30",
        "subtotal": total,
        "descount": 0.0,
        "shipping": 0.0,
        "seles_tax": 0.0,
        "total": total,
        "due_date": "2026-08-30T10:00:00",
        "invoice_doc": None,
    }


def test_create_invoice_returns_400_when_products_missing(client):
    response = client.post("/invoice", json={})

    assert response.status_code == 400

    data = response.get_json()
    assert data["success"] is False


@pytest.mark.parametrize(
    "payload",
    [
        {"products": []},
        {"products": None},
    ],
)
def test_create_invoice_returns_400_when_products_empty_or_none(client, payload):
    response = client.post("/invoice", json=payload)

    assert response.status_code == 400

    data = response.get_json()
    assert data["success"] is False


def test_create_invoice_returns_404_when_product_not_found(client, monkeypatch):
    product_service = Mock()
    invoice_service = Mock()

    product_service.get_a_product_by_id.return_value = None

    monkeypatch.setattr(invoice_routes, "product_service", product_service)
    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.post(
        "/invoice",
        json={
            "products": [{"id": "prod-1", "qty": 2}],
            "customer": "Customer A",
        },
    )

    assert response.status_code == 404

    product_service.get_a_product_by_id.assert_called_once_with("prod-1")
    product_service.decrease_qty.assert_not_called()
    invoice_service.add_invoice.assert_not_called()


def test_create_invoice_returns_400_when_stock_is_insufficient(client, monkeypatch):
    product_service = Mock()
    invoice_service = Mock()

    product_service.get_a_product_by_id.return_value = make_product_dict(qty=1)

    monkeypatch.setattr(invoice_routes, "product_service", product_service)
    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.post(
        "/invoice",
        json={
            "products": [{"id": "prod-1", "qty": 2}],
            "customer": "Customer A",
        },
    )

    assert response.status_code == 400

    product_service.get_a_product_by_id.assert_called_once_with("prod-1")
    product_service.decrease_qty.assert_not_called()
    invoice_service.add_invoice.assert_not_called()


def test_create_invoice_decreases_stock_and_saves_invoice(client, monkeypatch):
    product_service = Mock()
    invoice_service = Mock()

    product_service.get_a_product_by_id.return_value = make_product_dict(qty=10)

    monkeypatch.setattr(invoice_routes, "product_service", product_service)
    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.post(
        "/invoice",
        json={
            "invoice_id": "inv-1",
            "products": [{"id": "prod-1", "qty": 2}],
            "customer": "Customer A",
            "seller": "AirPart",
            "bill_to": "Customer Office",
            "ship_to": "Customer Warehouse",
            "terms": "Net 30",
            "subtotal": 200,
            "descount": 10,
            "shipping": 5,
            "seles_tax": 9,
            "total": 204,
            "due_date": "2026-08-30T10:00:00",
            "timestamp": "2026-08-01T10:00:00",
        },
    )

    assert response.status_code == 200

    assert product_service.get_a_product_by_id.call_count == 2
    product_service.get_a_product_by_id.assert_any_call("prod-1")

    product_service.decrease_qty.assert_called_once_with(product_id="prod-1", amount=2)
    invoice_service.add_invoice.assert_called_once()

    saved_invoice = invoice_service.add_invoice.call_args.args[0]
    response_data = response.get_json()["data"]

    assert saved_invoice == response_data
    assert saved_invoice["invoice_id"] == "inv-1"
    assert saved_invoice["customer"] == "Customer A"
    assert saved_invoice["products"] == [{"id": "prod-1", "qty": 2}]


def test_load_a_invoice_returns_invoice_when_found(client, monkeypatch):
    invoice_service = Mock()
    invoice_data = make_invoice_dict(invoice_id="inv-1")

    invoice_service.get_a_invoice_by_id.return_value = invoice_data

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.get("/invoice/inv-1")

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert data["data"] == invoice_data

    invoice_service.get_a_invoice_by_id.assert_called_once_with("inv-1")


def test_load_a_invoice_returns_404_when_invoice_not_found(client, monkeypatch):
    invoice_service = Mock()
    invoice_service.get_a_invoice_by_id.return_value = None

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.get("/invoice/missing-invoice")

    assert response.status_code == 404

    data = response.get_json()
    assert data["success"] is False

    invoice_service.get_a_invoice_by_id.assert_called_once_with("missing-invoice")


def test_delete_invoice_deletes_invoice_when_found(client, monkeypatch):
    invoice_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = make_invoice_dict("inv-1")

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.delete("/invoice/delete/inv-1")

    assert response.status_code == 200

    invoice_service.get_a_invoice_by_id.assert_called_once_with("inv-1")
    invoice_service.delete_a_invoice.assert_called_once_with("inv-1")


def test_delete_invoice_returns_404_when_invoice_not_found(client, monkeypatch):
    invoice_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = None

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.delete("/invoice/delete/missing-invoice")

    assert response.status_code == 404

    invoice_service.get_a_invoice_by_id.assert_called_once_with("missing-invoice")
    invoice_service.delete_a_invoice.assert_not_called()


def test_load_all_invoices_returns_serialized_invoices(client, monkeypatch):
    invoice_service = Mock()

    invoice_service.get_all_invoice.return_value = [
        make_invoice_dict(invoice_id="inv-1", customer="Customer A"),
        make_invoice_dict(invoice_id="inv-2", customer="Customer B"),
    ]

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.get("/invoices")

    assert response.status_code == 200

    data = response.get_json()
    assert data["success"] is True
    assert len(data["data"]) == 2
    assert data["data"][0]["invoice_id"] == "inv-1"
    assert data["data"][1]["invoice_id"] == "inv-2"


def test_load_all_invoices_falls_back_to_raw_data_on_serialization_error(
    client,
    monkeypatch,
):
    invoice_service = Mock()

    invoice_service.get_all_invoice.return_value = [
        make_invoice_dict(invoice_id="inv-good"),
        {"broken": "record"},
    ]

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)

    response = client.get("/invoices")

    assert response.status_code == 200

    data = response.get_json()["data"]

    assert len(data) == 2
    assert data[0]["invoice_id"] == "inv-good"
    assert data[1] == {"broken": "record"}


def test_edit_invoice_returns_404_when_old_invoice_not_found(client, monkeypatch):
    invoice_service = Mock()
    product_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = None

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)
    monkeypatch.setattr(invoice_routes, "product_service", product_service)

    response = client.put(
        "/invoice/edit/inv-1",
        json={"new_invoice": make_invoice_dict(invoice_id="inv-1")},
    )

    assert response.status_code == 404

    invoice_service.get_a_invoice_by_id.assert_called_once_with("inv-1")
    invoice_service.edit_invoice.assert_not_called()
    product_service.increase_qty.assert_not_called()
    product_service.decrease_qty.assert_not_called()


def test_edit_invoice_returns_400_when_new_invoice_missing(client, monkeypatch):
    invoice_service = Mock()
    product_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = make_invoice_dict(
        invoice_id="inv-1",
        products=[make_product_dict(qty=2)],
    )

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)
    monkeypatch.setattr(invoice_routes, "product_service", product_service)

    response = client.put("/invoice/edit/inv-1", json={})

    assert response.status_code == 400

    invoice_service.edit_invoice.assert_not_called()
    product_service.increase_qty.assert_not_called()
    product_service.decrease_qty.assert_not_called()


def test_edit_invoice_returns_404_when_new_product_not_found(client, monkeypatch):
    invoice_service = Mock()
    product_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = make_invoice_dict(
        invoice_id="inv-1",
        products=[make_product_dict(product_id="prod-1", qty=2)],
    )
    product_service.get_a_product_by_id.return_value = None

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)
    monkeypatch.setattr(invoice_routes, "product_service", product_service)

    response = client.put(
        "/invoice/edit/inv-1",
        json={
            "new_invoice": make_invoice_dict(
                invoice_id="inv-1",
                products=[make_product_dict(product_id="prod-2", qty=3)],
                customer="Updated Customer",
            )
        },
    )

    assert response.status_code == 404

    product_service.increase_qty.assert_called_once_with("prod-1", 2)
    product_service.get_a_product_by_id.assert_called_once_with("prod-2")
    product_service.decrease_qty.assert_not_called()
    invoice_service.edit_invoice.assert_not_called()


def test_edit_invoice_returns_400_when_new_stock_is_insufficient(
    client,
    monkeypatch,
):
    invoice_service = Mock()
    product_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = make_invoice_dict(
        invoice_id="inv-1",
        products=[make_product_dict(product_id="prod-1", qty=2)],
    )
    product_service.get_a_product_by_id.return_value = make_product_dict(
        product_id="prod-2",
        qty=1,
    )

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)
    monkeypatch.setattr(invoice_routes, "product_service", product_service)

    response = client.put(
        "/invoice/edit/inv-1",
        json={
            "new_invoice": make_invoice_dict(
                invoice_id="inv-1",
                products=[make_product_dict(product_id="prod-2", qty=3)],
                customer="Updated Customer",
            )
        },
    )

    assert response.status_code == 400

    product_service.increase_qty.assert_called_once_with("prod-1", 2)
    product_service.get_a_product_by_id.assert_called_once_with("prod-2")
    product_service.decrease_qty.assert_not_called()
    invoice_service.edit_invoice.assert_not_called()


def test_edit_invoice_restores_old_stock_then_applies_new_stock(
    client,
    monkeypatch,
):
    invoice_service = Mock()
    product_service = Mock()

    invoice_service.get_a_invoice_by_id.return_value = make_invoice_dict(
        invoice_id="inv-1",
        products=[make_product_dict(product_id="prod-1", qty=2)],
        customer="Old Customer",
        total=100.0,
    )
    product_service.get_a_product_by_id.return_value = make_product_dict(
        product_id="prod-2",
        qty=10,
    )

    monkeypatch.setattr(invoice_routes, "invoice_service", invoice_service)
    monkeypatch.setattr(invoice_routes, "product_service", product_service)

    response = client.put(
        "/invoice/edit/inv-1",
        json={
            "new_invoice": make_invoice_dict(
                invoice_id="inv-1",
                products=[make_product_dict(product_id="prod-2", qty=3)],
                customer="Updated Customer",
                total=300.0,
            )
        },
    )

    assert response.status_code == 200

    product_service.increase_qty.assert_called_once_with("prod-1", 2)
    product_service.get_a_product_by_id.assert_called_once_with("prod-2")
    product_service.decrease_qty.assert_called_once_with("prod-2", 3)
    invoice_service.edit_invoice.assert_called_once()

    product_calls = product_service.mock_calls

    assert product_calls.index(call.increase_qty("prod-1", 2)) < product_calls.index(
        call.get_a_product_by_id("prod-2")
    )
    assert product_calls.index(
        call.get_a_product_by_id("prod-2")
    ) < product_calls.index(call.decrease_qty("prod-2", 3))

    edited_invoice_id = invoice_service.edit_invoice.call_args.args[0]
    edited_invoice_data = invoice_service.edit_invoice.call_args.args[1]

    assert edited_invoice_id == "inv-1"
    assert edited_invoice_data["customer"] == "Updated Customer"
    assert edited_invoice_data["total"] == 300.0
