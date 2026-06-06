"""Run app space"""

from flasgger import Swagger
from flask import Flask
from flask_cors import CORS

from apis import invoice_bp, product_bp


def main():
    """Main app"""
    app = Flask(__name__)
    CORS(app)
    swagger = Swagger(app)
    app.register_blueprint(product_bp)
    app.register_blueprint(invoice_bp)
    app.run(host="127.0.0.1", port=5000, debug=True)


if __name__ == "__main__":
    main()
