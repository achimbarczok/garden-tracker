"""Unit tests for Flask routes (Tasks 4.4, 4.5)."""
import importlib
import os
import sys
import pytest

import db


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


# ---------------------------------------------------------------------------
# Example-based tests for chronologische-listen feature (Tasks 7.1–7.9)
# ---------------------------------------------------------------------------


def _add_plant_with_beobachtung(kategorie="Obst", ereignistyp="Blüte"):
    """Helper: add a plant with one Beobachtung, return plant_id."""
    db.add_plant("Testpflanze", "Obstbaum", None, "Sonne", None,
                 kategorie=kategorie)
    plants = db.get_all_plants()
    pid = plants[0]["id"]
    db.add_beobachtung(pid, 2024, ereignistyp, 3, 5, notiz="Testnotiz")
    return pid


def _add_plant_with_ereignis(kategorie="Obst", ereignistyp="Ernte"):
    """Helper: add a plant with one Ereignis, return plant_id."""
    db.add_plant("Testpflanze", "Obstbaum", None, "Sonne", None,
                 kategorie=kategorie)
    plants = db.get_all_plants()
    pid = plants[0]["id"]
    db.add_ereignis(pid, ereignistyp, 4, 6)
    return pid


def test_navigation_links(client):
    """GET / → HTML contains navigation links to /beobachtungen and /ereignisse.

    Requirements: 1.1, 1.2, 1.3
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'href="/beobachtungen"' in html
    assert 'href="/ereignisse"' in html


def test_filterleiste_beobachtungen(client):
    """GET /beobachtungen with data → HTML contains filter dropdowns.

    Requirements: 5.1
    """
    _add_plant_with_beobachtung()
    response = client.get("/beobachtungen")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'name="kategorie"' in html
    assert 'name="ereignis"' in html
    assert 'name="monat"' in html


def test_filterleiste_ereignisse(client):
    """GET /ereignisse with data → HTML contains filter dropdowns.

    Requirements: 6.1
    """
    _add_plant_with_ereignis()
    response = client.get("/ereignisse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'name="kategorie"' in html
    assert 'name="ereignis"' in html
    assert 'name="monat"' in html


def test_filter_reset_link_beobachtungen(client):
    """GET /beobachtungen?kategorie=Obst → HTML contains 'Filter zurücksetzen'.

    Requirements: 5.6
    """
    _add_plant_with_beobachtung(kategorie="Obst")
    response = client.get("/beobachtungen?kategorie=Obst")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Filter zurücksetzen" in html


def test_filter_reset_link_ereignisse(client):
    """GET /ereignisse?ereignis=Ernte → HTML contains 'Filter zurücksetzen'.

    Requirements: 6.6
    """
    _add_plant_with_ereignis(ereignistyp="Ernte")
    response = client.get("/ereignisse?ereignis=Ernte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Filter zurücksetzen" in html


def test_leerer_zustand_beobachtungen(client):
    """GET /beobachtungen without data → 'Noch keine Beobachtungen vorhanden.'

    Requirements: 7.1
    """
    response = client.get("/beobachtungen")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Noch keine Beobachtungen vorhanden." in html


def test_leerer_zustand_ereignisse(client):
    """GET /ereignisse without data → 'Noch keine Ereignisse vorhanden.'

    Requirements: 7.2
    """
    response = client.get("/ereignisse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Noch keine Ereignisse vorhanden." in html


def test_keine_treffer_beobachtungen(client):
    """Filter with no matches → 'Keine Beobachtungen gefunden.' + reset link.

    Requirements: 7.3
    """
    _add_plant_with_beobachtung(kategorie="Obst")
    response = client.get("/beobachtungen?kategorie=Gemüse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Keine Beobachtungen gefunden." in html
    assert "Filter zurücksetzen" in html


def test_keine_treffer_ereignisse(client):
    """Filter with no matches → 'Keine Ereignisse gefunden.' + reset link.

    Requirements: 7.4
    """
    _add_plant_with_ereignis(kategorie="Obst")
    response = client.get("/ereignisse?kategorie=Gemüse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Keine Ereignisse gefunden." in html
    assert "Filter zurücksetzen" in html
