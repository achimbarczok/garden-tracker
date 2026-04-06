"""Example-based tests for Pflanzen-Fotos feature (Tasks 9.1–9.11)."""
import importlib
import os
import pathlib
import sqlite3
from io import BytesIO

import pytest
from PIL import Image


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jpeg_bytes(width=100, height=100):
    """Create a minimal valid JPEG image in memory."""
    img = Image.new("RGB", (width, height), color="green")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


def _upload_foto(client, plant_id, jpeg_bytes=None, bezeichnung="", content_type="image/jpeg"):
    """Helper to POST a foto upload for a plant."""
    if jpeg_bytes is None:
        jpeg_bytes = _make_jpeg_bytes()
    data = {
        "foto": (BytesIO(jpeg_bytes), "test.jpg", content_type),
        "bezeichnung": bezeichnung,
    }
    return client.post(
        f"/plant/{plant_id}/foto/upload",
        data=data,
        content_type="multipart/form-data",
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def setup_db(tmp_path, monkeypatch):
    """Initialise a fresh DB in tmp_path and return the reloaded db module."""
    db_path = str(tmp_path / "test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    import db as db_module
    importlib.reload(db_module)
    db_module.init_db()
    return db_module


@pytest.fixture()
def client(setup_db, tmp_path, monkeypatch):
    """Flask test client with isolated DB and FOTOS_DIR."""
    import app as app_module
    importlib.reload(app_module)
    app_module.FOTOS_DIR = pathlib.Path(str(tmp_path)) / "fotos"
    os.makedirs(app_module.FOTOS_DIR, exist_ok=True)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture()
def plant_id(setup_db):
    """Create a test plant and return its id."""
    setup_db.add_plant(name="Testpflanze", type="Gemüse", variety=None,
                       lichtbedarf="Sonne", kommentar=None, kategorie="Gemüse")
    plants = setup_db.get_all_plants(include_inactive=True)
    return plants[-1]["id"]


# ---------------------------------------------------------------------------
# 9.1 Migration erstellt fotos-Tabelle mit korrekten Spalten
# ---------------------------------------------------------------------------

def test_migration_creates_fotos_table(tmp_path, monkeypatch):
    """After init_db(), the fotos table exists with correct columns.

    Requirements: 8.1, 8.2
    """
    db_path = str(tmp_path / "migrate_test.db")
    monkeypatch.setenv("DB_PATH", db_path)
    import db as db_module
    importlib.reload(db_module)
    db_module.init_db()

    conn = sqlite3.connect(db_path)
    cols = {row[1] for row in conn.execute("PRAGMA table_info(fotos)")}
    conn.close()

    assert "id" in cols
    assert "plant_id" in cols
    assert "dateiname" in cols
    assert "bezeichnung" in cols
    assert "ist_hauptbild" in cols


# ---------------------------------------------------------------------------
# 9.2 Upload-Formular auf Bearbeitungsseite vorhanden
# ---------------------------------------------------------------------------

def test_upload_form_present(client, plant_id):
    """GET /plant/<id>/edit contains upload form with enctype, file input, bezeichnung field.

    Requirements: 1.1, 1.3
    """
    response = client.get(f"/plant/{plant_id}/edit")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'enctype="multipart/form-data"' in html
    assert 'name="foto"' in html
    assert 'name="bezeichnung"' in html


# ---------------------------------------------------------------------------
# 9.3 Upload-Formular ausgeblendet bei 5 Fotos
# ---------------------------------------------------------------------------

def test_upload_form_hidden_at_max(client, plant_id):
    """Plant with 5 fotos → no upload form, hint 'Maximum von 5 Fotos erreicht'.

    Requirements: 3.2
    """
    for _ in range(5):
        resp = _upload_foto(client, plant_id)
        assert resp.status_code in (200, 302)

    response = client.get(f"/plant/{plant_id}/edit")
    html = response.data.decode("utf-8")
    assert "Maximum von 5 Fotos erreicht" in html
    # The upload form action should not be present when max is reached
    assert f'action="/plant/{plant_id}/foto/upload"' not in html


# ---------------------------------------------------------------------------
# 9.4 Löschen-Button pro Foto vorhanden
# ---------------------------------------------------------------------------

def test_delete_button_present(client, plant_id):
    """Plant with fotos → delete buttons present in HTML.

    Requirements: 5.1
    """
    _upload_foto(client, plant_id)
    response = client.get(f"/plant/{plant_id}/edit")
    html = response.data.decode("utf-8")
    assert "/foto/" in html
    assert "/remove" in html


# ---------------------------------------------------------------------------
# 9.5 Hauptbild-Button vorhanden
# ---------------------------------------------------------------------------

def test_hauptbild_button_present(client, plant_id):
    """Plant with multiple fotos → hauptbild buttons for non-hauptbilder.

    Requirements: 11.4
    """
    _upload_foto(client, plant_id)
    _upload_foto(client, plant_id)
    response = client.get(f"/plant/{plant_id}/edit")
    html = response.data.decode("utf-8")
    assert "/hauptbild" in html


# ---------------------------------------------------------------------------
# 9.6 Upload für nicht existierende Pflanze → 404
# ---------------------------------------------------------------------------

def test_upload_nonexistent_plant_404(client):
    """POST /plant/99999/foto/upload → HTTP 404.

    Requirements: 10.1
    """
    response = _upload_foto(client, 99999)
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# 9.7 Upload ohne Datei → Fehlermeldung
# ---------------------------------------------------------------------------

def test_no_file_error(client, plant_id):
    """POST without file → 'Bitte eine Bilddatei auswählen.'

    Requirements: 7.3
    """
    response = client.post(
        f"/plant/{plant_id}/foto/upload",
        data={},
        content_type="multipart/form-data",
    )
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Bitte eine Bilddatei auswählen." in html


# ---------------------------------------------------------------------------
# 9.8 Beschädigte Bilddatei → Fehlermeldung
# ---------------------------------------------------------------------------

def test_corrupt_image_error(client, plant_id):
    """POST with invalid file → 'Das Bild konnte nicht verarbeitet werden.'

    Requirements: 10.3
    """
    corrupt_data = b"this is not an image at all"
    response = _upload_foto(client, plant_id, jpeg_bytes=corrupt_data)
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Das Bild konnte nicht verarbeitet werden." in html


# ---------------------------------------------------------------------------
# 9.9 EXIF-Rotation wird korrekt angewendet
# ---------------------------------------------------------------------------

def test_exif_rotation(tmp_path):
    """Image with EXIF orientation → correct dimensions after process_image().

    Requirements: 2.4
    """
    import struct

    # Create a 100x200 portrait image
    img = Image.new("RGB", (100, 200), color="red")
    buf = BytesIO()

    # Build a minimal EXIF segment with Orientation tag = 6 (90° CW rotation)
    # EXIF structure: APP1 marker + Exif header + TIFF header + IFD with orientation
    # Using big-endian ("MM") TIFF format
    # IFD entry: tag=0x0112 (Orientation), type=3 (SHORT), count=1, value=6
    ifd_entry = struct.pack(">HHII", 0x0112, 3, 1, 6 << 16)
    ifd = struct.pack(">H", 1) + ifd_entry + struct.pack(">I", 0)  # 1 entry + next IFD offset
    tiff_header = b"MM" + struct.pack(">HI", 42, 8)  # big-endian, magic 42, offset to IFD
    exif_data = b"Exif\x00\x00" + tiff_header + ifd
    # APP1 marker: FF E1 + length (2 bytes, includes length itself)
    app1_length = len(exif_data) + 2
    app1 = b"\xff\xe1" + struct.pack(">H", app1_length) + exif_data

    # Save JPEG without EXIF first, then inject EXIF
    img.save(buf, format="JPEG")
    jpeg_bytes = buf.getvalue()
    # Insert APP1 right after SOI marker (first 2 bytes: FF D8)
    exif_jpeg = jpeg_bytes[:2] + app1 + jpeg_bytes[2:]

    buf2 = BytesIO(exif_jpeg)

    import app as app_module
    result_bytes = app_module.process_image(buf2)

    result_img = Image.open(BytesIO(result_bytes))
    # After EXIF transpose of orientation 6 on a 100x200 image,
    # the result should be 200x100
    assert result_img.size == (200, 100)


# ---------------------------------------------------------------------------
# 9.10 Foto-Auslieferung über /fotos/<dateiname>
# ---------------------------------------------------------------------------

def test_serve_foto_route(client, plant_id, setup_db):
    """GET /fotos/<dateiname> → status 200, image served.

    Requirements: 4.3
    """
    _upload_foto(client, plant_id)
    fotos = setup_db.get_fotos(plant_id)
    assert len(fotos) == 1
    dateiname = fotos[0]["dateiname"]

    response = client.get(f"/fotos/{dateiname}")
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# 9.11 Dateisystemfehler hinterlässt keine partiellen DB-Einträge
# ---------------------------------------------------------------------------

def test_filesystem_error_no_partial_db(client, plant_id, monkeypatch, setup_db):
    """Simulated filesystem error → no DB entry for the foto.

    Requirements: 10.2
    """
    original_write_bytes = pathlib.Path.write_bytes

    def _failing_write_bytes(self, data):
        # Only fail for files in the fotos directory
        if "fotos" in str(self):
            raise OSError("Simulated disk error")
        return original_write_bytes(self, data)

    monkeypatch.setattr(pathlib.Path, "write_bytes", _failing_write_bytes)

    response = _upload_foto(client, plant_id)
    # The upload should fail (400 with error message)
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Fehler beim Speichern" in html

    # No foto should be in the DB
    fotos = setup_db.get_fotos(plant_id)
    assert len(fotos) == 0
