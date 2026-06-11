from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from .apis.routes.invoice import invoice_bp
from .apis.routes.product import product_bp


def create_app():
    """Create app instance"""

    app = Flask(__name__)
    CORS(app)
    Swagger(app)
    app.register_blueprint(product_bp)
    app.register_blueprint(invoice_bp)

    return app
