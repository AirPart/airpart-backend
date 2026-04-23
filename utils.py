"""Utils for us in app"""

import uuid
from datetime import datetime

from flask import jsonify


def idgen():
    """Generate uuid for product"""
    return uuid.uuid4()


def timestampgen() -> float:
    """Generate timestamp from now datetime"""
    now = datetime.now()
    return datetime.timestamp(now)


def json_response(success: bool, message: str, data=None, errors=None) -> dict:
    """Return estandard response"""
    response = {
        "success": success,
        "message": message,
    }
    if data is not None:
        response["data"] = data
    if errors is not None:
        response["errors"] = errors
    return jsonify(response)
