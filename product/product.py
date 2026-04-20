"""Managing products"""

from utils import idgen, timestampgen


class Product:
    """Product object for create a product"""

    def __init__(self, portnumber: str, name: str, total: int) -> None:
        self.portnumber = portnumber
        self.name = name
        self.total = total

        self.id = str(idgen())
        self.image = None
        self.timestamp = timestampgen()
