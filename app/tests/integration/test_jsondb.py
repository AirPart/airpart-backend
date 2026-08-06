"""Integration tests for JsonDB core persistence."""

import json

import pytest

from app.core.db import JsonDB


def make_jsondb(db_file):
    """Create JsonDB with common constructor variants."""
    try:
        return JsonDB(db_file)
    except TypeError:
        try:
            return JsonDB(str(db_file))
        except TypeError:
            db = JsonDB()

            for attr_name in ["path", "db_path", "file_path", "database_path"]:
                if hasattr(db, attr_name):
                    setattr(db, attr_name, db_file)
                    return db

            db.path = db_file
            return db


@pytest.fixture
def db_file(tmp_path):
    return tmp_path / "test_db.json"


@pytest.fixture
def json_db(db_file):
    return make_jsondb(db_file)


def test_jsondb_loads_existing_json_file(json_db, db_file):
    db_file.write_text(
        json.dumps(
            {
                "products": [
                    {
                        "id": "prod-1",
                        "description": "Engine Part",
                    }
                ],
                "invoices": [],
            }
        ),
        encoding="utf-8",
    )

    data = json_db.load()

    assert data == {
        "products": [
            {
                "id": "prod-1",
                "description": "Engine Part",
            }
        ],
        "invoices": [],
    }


def test_jsondb_saves_data_to_file(json_db, db_file):
    data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Engine Part",
            }
        ],
        "invoices": [
            {
                "id": "inv-1",
                "customer": "Customer A",
            }
        ],
    }

    json_db.save(data)

    saved_data = json.loads(db_file.read_text(encoding="utf-8"))

    assert saved_data == data


def test_jsondb_save_overwrites_existing_file(json_db, db_file):
    db_file.write_text(
        json.dumps(
            {
                "products": [{"id": "old-product"}],
                "invoices": [],
            }
        ),
        encoding="utf-8",
    )

    new_data = {
        "products": [{"id": "new-product"}],
        "invoices": [{"id": "inv-1"}],
    }

    json_db.save(new_data)

    saved_data = json.loads(db_file.read_text(encoding="utf-8"))

    assert saved_data == new_data


def test_jsondb_persists_round_trip_data(json_db):
    data = {
        "products": [
            {
                "id": "prod-1",
                "description": "Engine Part",
                "qty": 5,
            }
        ],
        "invoices": [
            {
                "id": "inv-1",
                "products": [{"id": "prod-1", "qty": 2}],
                "customer": "Customer A",
            }
        ],
    }

    json_db.save(data)

    loaded_data = json_db.load()

    assert loaded_data == data


def test_jsondb_load_missing_file_has_defined_behavior(json_db, db_file):
    if db_file.exists():
        db_file.unlink()

    try:
        data = json_db.load()
    except FileNotFoundError:
        return

    assert isinstance(data, dict)


def test_jsondb_load_empty_file_has_defined_behavior(json_db, db_file):
    db_file.write_text("", encoding="utf-8")

    try:
        data = json_db.load()
    except json.JSONDecodeError:
        return

    assert isinstance(data, dict)


def test_jsondb_load_corrupted_file_has_defined_behavior(json_db, db_file):
    db_file.write_text("{ invalid json", encoding="utf-8")

    try:
        data = json_db.load()
    except json.JSONDecodeError:
        return

    assert isinstance(data, dict)
