"""Unit tests for Flask routes (Tasks 4.4, 4.5)."""
import importlib
import os
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
    assert "Noch keine Pflanzen vorhanden." in response.data.decode("utf-8")


def test_german_error_messages(client):
    """POST /add with blank name → HTTP 400 with German error text.

    Requirements: 3.1, 3.2
    """
    response = client.post("/add", data={"name": "   ", "type": "Obst", "variety": ""})
    assert response.status_code == 400
    assert "Name darf nicht leer sein." in response.data.decode("utf-8")


# ---------------------------------------------------------------------------
# Example-based tests for pflanze-inaktiv feature (Tasks 9.1–9.4)
# ---------------------------------------------------------------------------


def test_deactivate_nonexistent_404(client):
    """POST /plant/99999/deactivate with non-existent ID → HTTP 404.

    Requirements: 8.1
    """
    response = client.post("/plant/99999/deactivate")
    assert response.status_code == 404


def test_activate_nonexistent_404(client):
    """POST /plant/99999/activate with non-existent ID → HTTP 404.

    Requirements: 8.1
    """
    response = client.post("/plant/99999/activate")
    assert response.status_code == 404


def test_filter_checkbox_present(client):
    """GET / contains the 'Inaktive anzeigen' checkbox.

    Requirements: 4.2
    """
    # Add a plant so the filter bar is rendered
    client.post("/add", data={
        "name": "Testpflanze",
        "type": "Obst",
        "variety": "",
        "kategorie": "Obst",
        "lichtbedarf": "Sonne",
    })
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Inaktive anzeigen" in html
    assert 'name="show_inactive"' in html


def test_migration_adds_aktiv_column(tmp_path, monkeypatch):
    """Migration adds 'aktiv' column; existing plants get aktiv = 1.

    Requirements: 1.4
    """
    import sqlite3

    db_file = str(tmp_path / "migrate_test.db")
    monkeypatch.setenv("DB_PATH", db_file)

    # Create a minimal plants table WITHOUT the aktiv column
    conn = sqlite3.connect(db_file)
    conn.execute(
        "CREATE TABLE plants ("
        "  id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "  name TEXT NOT NULL,"
        "  type TEXT NOT NULL,"
        "  variety TEXT"
        ")"
    )
    conn.execute("INSERT INTO plants (name, type) VALUES ('Tomate', 'Gemüse')")
    conn.execute("INSERT INTO plants (name, type) VALUES ('Basilikum', 'Kräuter')")
    conn.commit()
    conn.close()

    # Now reload db module and run init_db which triggers _migrate
    import db
    importlib.reload(db)
    db.init_db()

    # Verify aktiv column exists and all existing plants have aktiv = 1
    conn2 = sqlite3.connect(db_file)
    conn2.row_factory = sqlite3.Row
    rows = conn2.execute("SELECT name, aktiv FROM plants").fetchall()
    conn2.close()

    assert len(rows) == 2
    for row in rows:
        assert row["aktiv"] == 1, (
            f"Expected aktiv=1 for existing plant '{row['name']}', got {row['aktiv']}"
        )
