from flask import jsonify


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
