"""Unit tests for InvoiceService."""

from unittest.mock import MagicMock

from app.services.invoice import InvoiceService


def make_service():
    """Create InvoiceService with mocked repository."""
    mock_repo = MagicMock()
    service = InvoiceService(repo=mock_repo)
    return service, mock_repo


# ==============================================================================
# Get invoices
# ==============================================================================


def test_get_all_invoice_returns_repo_invoices():
    service, mock_repo = make_service()

    expected_invoices = [
        {"id": "invoice-1", "customer": "Customer 1"},
        {"id": "invoice-2", "customer": "Customer 2"},
    ]
    mock_repo.get_all.return_value = expected_invoices

    result = service.get_all_invoice()

    assert result == expected_invoices
    mock_repo.get_all.assert_called_once_with()


def test_get_a_invoice_by_id_returns_repo_invoice():
    service, mock_repo = make_service()

    expected_invoice = {
        "id": "invoice-1",
        "customer": "Customer 1",
    }
    mock_repo.get_by_id.return_value = expected_invoice

    result = service.get_a_invoice_by_id("invoice-1")

    assert result == expected_invoice
    mock_repo.get_by_id.assert_called_once_with(invoice_id="invoice-1")


def test_get_a_invoice_by_id_returns_none_when_invoice_not_found():
    service, mock_repo = make_service()

    mock_repo.get_by_id.return_value = None

    result = service.get_a_invoice_by_id("missing-invoice")

    assert result is None
    mock_repo.get_by_id.assert_called_once_with(invoice_id="missing-invoice")


# ==============================================================================
# Add invoice
# ==============================================================================


def test_add_invoice_calls_repository_add():
    service, mock_repo = make_service()

    invoice = MagicMock()

    result = service.add_invoice(invoice)

    assert result is None
    mock_repo.add.assert_called_once_with(invoice)


# ==============================================================================
# Delete invoice
# ==============================================================================


def test_delete_a_invoice_calls_repository_delete():
    service, mock_repo = make_service()

    result = service.delete_a_invoice("invoice-1")

    assert result is None
    mock_repo.delete.assert_called_once_with(invoice_id="invoice-1")


# ==============================================================================
# Edit invoice
# ==============================================================================


def test_edit_invoice_calls_repository_update():
    service, mock_repo = make_service()

    new_invoice = MagicMock()

    result = service.edit_invoice(
        invoice_id="invoice-1",
        new_invoice=new_invoice,
    )

    assert result is None
    mock_repo.update.assert_called_once_with(
        invoice_id="invoice-1",
        new_invoice=new_invoice,
    )
