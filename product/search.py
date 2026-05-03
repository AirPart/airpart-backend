"""Search api"""


class SearchAPI:
    """Search api class"""

    def __init__(self, query) -> None:
        self.query = query

    def parse_search(self):
        """Parse search from query"""
        parts = self.query.split(".")
        parts += [""] * (6 - len(parts))
        return parts[:6]

    def normalize(self, s: str):
        """Normalize value in filter send"""
        return (s or "").strip()

    def product_matches(self, product: dict, filters: dict):
        """Matches product with filters"""
        for key, val in filters.items():
            if not val:
                continue
            if product.get(key, "") != val:
                return False
        return True

    def search_products(self, products: list):
        """Search product with filters chooise"""
        description, part_number, serial_number, unit, alternate, company = (
            self.parse_search() + [""]
        )[:6]

        filters = {
            "description": self.normalize(description),
            "part_number": self.normalize(part_number),
            "serial_number": self.normalize(serial_number),
            "unit": self.normalize(unit),
            "alternate": self.normalize(alternate),
            "company": self.normalize(company),
        }

        result = []

        for product in products:
            if self.product_matches(product, filters):
                result.append(product)
        return result
