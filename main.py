"""Run app space"""

from flask import Flask

from apis import product_bp


def main():
    """Main app"""
    app = Flask(__name__)
    app.register_blueprint(product_bp)
    app.run(host="127.0.0.1", port=5000, debug=True)


if __name__ == "__main__":
    main()
