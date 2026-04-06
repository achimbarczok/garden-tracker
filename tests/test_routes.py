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
    assert "Noch keine Tagebucheinträge vorhanden." in html


def test_leerer_zustand_ereignisse(client):
    """GET /ereignisse without data → 'Noch keine Ereignisse vorhanden.'

    Requirements: 7.2
    """
    response = client.get("/ereignisse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Noch keine Einträge im Jahresplan." in html


def test_keine_treffer_beobachtungen(client):
    """Filter with no matches → 'Keine Beobachtungen gefunden.' + reset link.

    Requirements: 7.3
    """
    _add_plant_with_beobachtung(kategorie="Obst")
    response = client.get("/beobachtungen?kategorie=Gemüse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Keine Tagebucheinträge gefunden." in html
    assert "Filter zurücksetzen" in html


def test_keine_treffer_ereignisse(client):
    """Filter with no matches → 'Keine Ereignisse gefunden.' + reset link.

    Requirements: 7.4
    """
    _add_plant_with_ereignis(kategorie="Obst")
    response = client.get("/ereignisse?kategorie=Gemüse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Keine Einträge gefunden." in html
    assert "Filter zurücksetzen" in html


# ---------------------------------------------------------------------------
# Example-based tests for gartenkarte feature (Tasks 8.1–8.15)
# ---------------------------------------------------------------------------

import pathlib
import sqlite3


def _make_jpeg_bytes(width=100, height=100):
    """Create minimal JPEG bytes for testing."""
    from io import BytesIO
    from PIL import Image
    img = Image.new("RGB", (width, height), (100, 150, 200))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def _upload_kartenbild(client):
    """Upload a test kartenbild and return the response."""
    from io import BytesIO
    img_bytes = _make_jpeg_bytes()
    return client.post(
        "/gartenkarte/bild/upload",
        data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
        content_type="multipart/form-data",
    )


def test_karte_migration_creates_tables(tmp_path, monkeypatch):
    """8.1: After init_db(), kartenbild and kartenpositionen exist with correct columns.

    Requirements: 7.1, 7.2, 7.4
    """
    db_file = str(tmp_path / "migrate_karte.db")
    monkeypatch.setenv("DB_PATH", db_file)

    import db as db_mod
    importlib.reload(db_mod)
    db_mod.init_db()

    conn = sqlite3.connect(db_file)
    # Check kartenbild columns
    kb_cols = {row[1] for row in conn.execute("PRAGMA table_info(kartenbild)")}
    assert "id" in kb_cols
    assert "dateiname" in kb_cols

    # Check kartenpositionen columns
    kp_cols = {row[1] for row in conn.execute("PRAGMA table_info(kartenpositionen)")}
    assert "id" in kp_cols
    assert "plant_id" in kp_cols
    assert "x" in kp_cols
    assert "y" in kp_cols
    conn.close()


def test_karte_upload_form_when_no_image(client):
    """8.2: GET /gartenkarte without kartenbild → HTML contains upload form.

    Requirements: 1.1
    """
    response = client.get("/gartenkarte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'enctype="multipart/form-data"' in html


def test_karte_upload_no_file_error(client):
    """8.3: POST /gartenkarte/bild/upload without file → error message.

    Requirements: 1.6
    """
    response = client.post("/gartenkarte/bild/upload",
                           data={},
                           content_type="multipart/form-data")
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Bitte eine Bilddatei auswählen." in html


def test_karte_exif_rotation(tmp_path, monkeypatch):
    """8.4: EXIF orientation tag 6 (90° CW) → dimensions transposed after processing.

    Requirements: 2.4
    """
    from io import BytesIO
    from PIL import Image
    import struct

    db_file = str(tmp_path / "exif_test.db")
    monkeypatch.setenv("DB_PATH", db_file)

    import db as db_mod
    importlib.reload(db_mod)
    db_mod.init_db()

    import app as app_module
    importlib.reload(app_module)

    # Create a 100x200 image with EXIF orientation 6 (rotated 90° CW)
    # Build minimal EXIF with orientation tag = 6
    # EXIF structure: APP1 marker with TIFF header and IFD0 containing orientation
    def _make_exif_orientation(orientation):
        """Build minimal EXIF bytes with given orientation value."""
        # TIFF header (little-endian)
        tiff_header = b"II"  # little-endian
        tiff_header += struct.pack("<H", 42)  # magic
        tiff_header += struct.pack("<I", 8)   # offset to IFD0

        # IFD0 with one entry: Orientation (tag 0x0112)
        ifd = struct.pack("<H", 1)  # number of entries
        ifd += struct.pack("<HHI", 0x0112, 3, 1)  # tag, SHORT type, count
        ifd += struct.pack("<HH", orientation, 0)   # value (padded to 4 bytes)
        ifd += struct.pack("<I", 0)  # next IFD offset (none)

        tiff_data = tiff_header + ifd
        # Exif header: "Exif\x00\x00" + TIFF data
        exif_payload = b"Exif\x00\x00" + tiff_data
        return exif_payload

    img = Image.new("RGB", (100, 200), (50, 100, 150))
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    jpeg_bytes = buf.getvalue()

    # Inject EXIF APP1 segment right after SOI marker
    exif_payload = _make_exif_orientation(6)
    app1_marker = b"\xff\xe1"
    app1_length = struct.pack(">H", len(exif_payload) + 2)
    exif_segment = app1_marker + app1_length + exif_payload

    # JPEG starts with FFD8; insert EXIF right after
    modified_jpeg = jpeg_bytes[:2] + exif_segment + jpeg_bytes[2:]

    input_buf = BytesIO(modified_jpeg)
    result_bytes = app_module.process_kartenbild(input_buf)

    result_img = Image.open(BytesIO(result_bytes))
    # After transposing orientation 6 on a 100x200 image → 200x100
    assert result_img.size == (200, 100)


def test_karte_replace_button_present(client, tmp_path, monkeypatch):
    """8.5: Upload kartenbild, then GET /gartenkarte → HTML contains 'Bild ersetzen'.

    Requirements: 3.1
    """
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    _upload_kartenbild(client)
    response = client.get("/gartenkarte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Bild ersetzen" in html


def test_karte_delete_button_present(client, tmp_path, monkeypatch):
    """8.6: Upload kartenbild, then GET /gartenkarte → HTML contains 'Bild löschen'.

    Requirements: 3.3
    """
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    _upload_kartenbild(client)
    response = client.get("/gartenkarte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Bild löschen" in html


def test_karte_dropdown_shows_active_plants(client, tmp_path, monkeypatch):
    """8.7: Add a plant, upload kartenbild, GET /gartenkarte → dropdown with plant name.

    Requirements: 4.1
    """
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    # Add a plant first
    client.post("/add", data={
        "name": "Kartoffel",
        "type": "Gemüse",
        "variety": "",
        "kategorie": "Gemüse",
        "lichtbedarf": "Sonne",
    })

    _upload_kartenbild(client)
    response = client.get("/gartenkarte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Kartoffel" in html
    assert "<select" in html


def test_karte_nonexistent_plant_404(client, tmp_path, monkeypatch):
    """8.8: POST /gartenkarte/position/add with plant_id=99999 → HTTP 404.

    Requirements: 4.5
    """
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    _upload_kartenbild(client)
    response = client.post("/gartenkarte/position/add", data={
        "plant_id": "99999",
        "x": "50.0",
        "y": "50.0",
    })
    assert response.status_code == 404


def test_karte_remove_button_per_marker(client, tmp_path, monkeypatch):
    """8.9: Upload kartenbild, add plant + position, GET → marker-remove-btn present.

    Requirements: 6.1
    """
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    # Add a plant
    client.post("/add", data={
        "name": "Tomate",
        "type": "Gemüse",
        "variety": "",
        "kategorie": "Gemüse",
        "lichtbedarf": "Sonne",
    })

    _upload_kartenbild(client)

    # Get plant id
    import db as db_mod
    plants = db_mod.get_all_plants()
    plant_id = plants[0]["id"]

    # Add a position
    client.post("/gartenkarte/position/add", data={
        "plant_id": str(plant_id),
        "x": "25.0",
        "y": "75.0",
    })

    response = client.get("/gartenkarte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "marker-remove-btn" in html


def test_karte_nav_link_present(client):
    """8.10: GET / → HTML contains href="/gartenkarte" and "🗺️ Karte".

    Requirements: 9.1
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'href="/gartenkarte"' in html
    assert "Karte" in html


def test_karte_nav_link_active(client):
    """8.11: GET /gartenkarte → HTML contains nav-active on the Karte link.

    Requirements: 9.3
    """
    response = client.get("/gartenkarte")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "nav-active" in html


def test_karte_position_without_kartenbild_error(client):
    """8.12: POST /gartenkarte/position/add without kartenbild → error message.

    Requirements: 11.4
    """
    response = client.post("/gartenkarte/position/add", data={
        "plant_id": "1",
        "x": "50.0",
        "y": "50.0",
    })
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Bitte zuerst ein Kartenbild hochladen." in html


def test_karte_corrupt_image_error(client):
    """8.13: POST with corrupted file data → error message.

    Requirements: 11.2
    """
    from io import BytesIO
    response = client.post(
        "/gartenkarte/bild/upload",
        data={"bild": (BytesIO(b"not-an-image-at-all"), "bad.jpg", "image/jpeg")},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Das Bild konnte nicht verarbeitet werden." in html


def test_karte_serve_kartenbild(client, tmp_path, monkeypatch):
    """8.14: Upload kartenbild, then GET /karte/<dateiname> → status 200.

    Requirements: 8.1
    """
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    _upload_kartenbild(client)

    import db as db_mod
    kb = db_mod.get_kartenbild()
    assert kb is not None

    response = client.get(f"/karte/{kb['dateiname']}")
    assert response.status_code == 200


def test_karte_filesystem_error_no_partial_db(client, tmp_path, monkeypatch):
    """8.15: Mock write_bytes to raise OSError → no DB entry in kartenbild.

    Requirements: 11.1
    """
    from io import BytesIO
    from unittest.mock import patch
    import app as app_module
    app_module.KARTE_DIR = pathlib.Path(tmp_path) / "karte"
    os.makedirs(app_module.KARTE_DIR, exist_ok=True)

    img_bytes = _make_jpeg_bytes()

    with patch.object(pathlib.Path, "write_bytes", side_effect=OSError("disk full")):
        response = client.post(
            "/gartenkarte/bild/upload",
            data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Fehler beim Speichern der Datei." in html

    import db as db_mod
    kb = db_mod.get_kartenbild()
    assert kb is None
