"""Run app space"""

from app import create_app


def main():
    """Main app"""

    app = create_app()
    app.run(host="127.0.0.1", port=5000, debug=True)


if __name__ == "__main__":
    main()
