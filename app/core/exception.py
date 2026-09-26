"""Domain and business logic exceptions"""


class AppException(Exception):
    """Base exception for application domain errors"""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class NotFoundError(AppException):
    """Resource not found base error"""

    pass


class ValidationError(AppException):
    """Business validation error"""

    pass


class ProductNotFoundError(NotFoundError):
    """Raised when a requested product does not exist in the database"""

    def __init__(self, product_id: str) -> None:
        super().__init__(f"Product with ID '{product_id}' not found.")
        self.product_id = product_id


class InvoiceNotFoundError(NotFoundError):
    """Raised when an invoice is not found"""

    def __init__(self, invoice_id: str) -> None:
        super().__init__(f"Invoice with ID '{invoice_id}' not found.")
        self.invoice_id = invoice_id


class InsufficientStockError(ValidationError):
    """Raised when available stock is less than requested quantity"""

    def __init__(self, product_id: str, available_qty: int, requested_qty: int) -> None:
        message = (
            f"Not enough stock for product '{product_id}'."
            f"Available: {available_qty}, Requested: {requested_qty}"
        )
        super().__init__(message)
        self.product_id = product_id
        self.available_qty = available_qty
        self.requested_qty = requested_qty
