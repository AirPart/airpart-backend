"""Managing products"""

from utils import timestampgen


class Product:
    def __init__(self, portnumber: str, name: str, total: int) -> None:
        self.portnumber = portnumber
        self.name = name
        self.total = total

        self.image = None
        self.timestamp = timestampgen()
