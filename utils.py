"""Utils for us in app"""

import uuid
from datetime import datetime


def idgen():
    """Generate uuid for product"""
    return uuid.uuid4()


def timestampgen() -> float:
    """Generate timestamp from now datetime"""
    now = datetime.now()
    return datetime.timestamp(now)
