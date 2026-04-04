"""Unit tests for Flask routes (Tasks 4.4, 4.5)."""
import os
import importlib
import sys
import pytest


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """Flask test client backed by a temporary SQLite database."""
    db_file = str(tmp_path / "test_plants.db")
    monkeypatch.setenv("DB_PATH", db_file)

    # Force reload of db and app modules so they pick up the new DB_PATH
    import db
    importlib.reload(db)

    import app as app_module
    importlib.reload(app_module)

    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_empty_state_message(client):
    """Empty DB → GET / returns 200 with German empty-state text.

    Requirements: 1.6, 3.2
    """
    response = client.get("/")
    assert response.status_code == 200
    assert "Keine Pflanzen vorhanden." in response.data.decode("utf-8")


def test_german_error_messages(client):
    """POST /add with blank name → HTTP 400 with German error text.

    Requirements: 3.1, 3.2
    """
    response = client.post("/add", data={"name": "   ", "type": "Obst", "variety": ""})
    assert response.status_code == 400
    assert "Name und Typ dürfen nicht leer sein." in response.data.decode("utf-8")
