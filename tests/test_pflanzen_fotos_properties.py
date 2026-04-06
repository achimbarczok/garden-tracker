"""Property-based tests for the pflanzen-fotos feature (Hypothesis).

# Feature: pflanzen-fotos
"""
import importlib
import os
import pathlib
import tempfile

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from io import BytesIO
from PIL import Image


# ---------------------------------------------------------------------------
# Strategies for valid plant data
# ---------------------------------------------------------------------------

VALID_LICHTBEDARF = ["Sonne", "Halbschatten", "Schatten"]
VALID_KATEGORIEN = ["Obst", "Gemüse", "Kräuter", "Stauden", "Sträucher", "Bäume", "Blumen", "Gründüngung", "Gartenpflege"]

plant_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
    min_size=1,
    max_size=50,
).filter(lambda s: s.strip() != "")

plant_type_st = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
    min_size=1,
    max_size=30,
).filter(lambda s: s.strip() != "")

lichtbedarf_st = st.sampled_from(VALID_LICHTBEDARF)
kategorie_st = st.sampled_from(VALID_KATEGORIEN)
optional_text_st = st.one_of(st.none(), st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
    min_size=1, max_size=30,
).filter(lambda s: s.strip() != ""))

bezeichnung_st = st.one_of(st.none(), st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
    min_size=1, max_size=30,
).filter(lambda s: s.strip() != ""))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_db(db_path: str):
    """Initialise an isolated SQLite database and return the reloaded db module."""
    os.environ["DB_PATH"] = db_path

    import db as db_module
    importlib.reload(db_module)
    db_module.init_db()
    return db_module


def _init_app(db_path: str):
    """Reload app module with correct DB_PATH and FOTOS_DIR, return (app_module, client)."""
    import app as app_module
    importlib.reload(app_module)
    app_module.FOTOS_DIR = pathlib.Path(db_path).parent / "fotos"
    os.makedirs(app_module.FOTOS_DIR, exist_ok=True)
    app_module.app.config["TESTING"] = True
    return app_module, app_module.app.test_client()


def _make_jpeg_bytes(width=100, height=100):
    """Create a minimal valid JPEG in memory."""
    img = Image.new("RGB", (width, height), color="green")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.getvalue()


def _make_png_bytes(width=100, height=100):
    """Create a minimal valid PNG in memory."""
    img = Image.new("RGB", (width, height), color="blue")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()


def _create_plant(db, name="Testpflanze", kategorie="Gemüse"):
    """Create a plant and return its id."""
    db.add_plant(
        name=name, type="Typ", variety=None,
        lichtbedarf="Sonne", kommentar=None, kategorie=kategorie,
    )
    plants = db.get_all_plants(include_inactive=True)
    return plants[-1]["id"]


def _upload_foto(client, plant_id, jpeg_bytes=None, bezeichnung=None, content_type="image/jpeg", filename="test.jpg"):
    """Upload a foto via Flask test client and return the response."""
    if jpeg_bytes is None:
        jpeg_bytes = _make_jpeg_bytes()
    data = {
        "foto": (BytesIO(jpeg_bytes), filename),
    }
    if bezeichnung is not None:
        data["bezeichnung"] = bezeichnung
    return client.post(
        f"/plant/{plant_id}/foto/upload",
        data=data,
        content_type="multipart/form-data",
        follow_redirects=False,
    )


# ---------------------------------------------------------------------------
# Property 1: Bildverkleinerung und JPEG-Konvertierung
# Feature: pflanzen-fotos, Property 1: Bildverkleinerung und JPEG-Konvertierung
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    width=st.integers(min_value=1, max_value=5000),
    height=st.integers(min_value=1, max_value=5000),
)
def test_image_resize_and_jpeg(width, height):
    """For any valid input image with arbitrary dimensions, after processing
    through process_image(), the result is a valid JPEG, the long side equals
    min(original_long_side, 640), and the aspect ratio is preserved proportionally.

    # Feature: pflanzen-fotos, Property 1: Bildverkleinerung und JPEG-Konvertierung

    **Validates: Requirements 2.1, 2.2, 2.3**
    """
    # Create a test image in memory
    img = Image.new("RGB", (width, height), color="red")
    buf = BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)

    # Import and call process_image
    import app as app_module
    result_bytes = app_module.process_image(buf)

    # Verify result is valid JPEG
    result_img = Image.open(BytesIO(result_bytes))
    assert result_img.format == "JPEG", f"Expected JPEG, got {result_img.format}"

    result_w, result_h = result_img.size
    original_long_side = max(width, height)
    expected_long_side = min(original_long_side, 640)

    # The long side of the result should equal expected
    result_long_side = max(result_w, result_h)
    assert result_long_side == expected_long_side, (
        f"Expected long side {expected_long_side}, got {result_long_side} "
        f"(original {width}x{height})"
    )

    # Aspect ratio: for images that were resized, check proportionality
    if original_long_side > 640:
        scale = 640 / original_long_side
        expected_w = max(1, int(width * scale))
        expected_h = max(1, int(height * scale))
        # Allow ±1 pixel rounding tolerance
        assert abs(result_w - expected_w) <= 1, (
            f"Width mismatch: expected ~{expected_w}, got {result_w}"
        )
        assert abs(result_h - expected_h) <= 1, (
            f"Height mismatch: expected ~{expected_h}, got {result_h}"
        )
    else:
        # Image should not be resized
        assert result_w == width and result_h == height, (
            f"Image should not be resized: expected {width}x{height}, got {result_w}x{result_h}"
        )


# ---------------------------------------------------------------------------
# Property 2: Upload ordnet Foto der richtigen Pflanze zu
# Feature: pflanzen-fotos, Property 2: Upload ordnet Foto der richtigen Pflanze zu
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    bezeichnung=bezeichnung_st,
)
def test_upload_assigns_to_plant(name, kategorie, bezeichnung):
    """For any valid image and any existing plant, after a successful upload
    the new foto in the DB has the correct plant_id and bezeichnung.

    # Feature: pflanzen-fotos, Property 2: Upload ordnet Foto der richtigen Pflanze zu

    **Validates: Requirements 1.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes, bezeichnung=bezeichnung)

        fotos = db.get_fotos(plant_id)
        assert len(fotos) == 1, f"Expected 1 foto, got {len(fotos)}"
        foto = fotos[0]
        assert foto["plant_id"] == plant_id, (
            f"Expected plant_id={plant_id}, got {foto['plant_id']}"
        )
        # bezeichnung: empty string or None from form → stored as None
        expected_bez = bezeichnung.strip() if bezeichnung and bezeichnung.strip() else None
        assert foto["bezeichnung"] == expected_bez, (
            f"Expected bezeichnung={expected_bez!r}, got {foto['bezeichnung']!r}"
        )


# ---------------------------------------------------------------------------
# Property 3: Redirect nach Foto-Operationen
# Feature: pflanzen-fotos, Property 3: Redirect nach Foto-Operationen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
)
def test_redirect_after_foto_ops(name, kategorie):
    """For any successful foto operation (upload, delete, set hauptbild),
    the application returns HTTP 302 redirect to /plant/<plant_id>/edit.

    # Feature: pflanzen-fotos, Property 3: Redirect nach Foto-Operationen

    **Validates: Requirements 1.4, 5.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        # Upload → 302
        resp_upload = _upload_foto(client, plant_id)
        assert resp_upload.status_code == 302, (
            f"Expected 302 for upload, got {resp_upload.status_code}"
        )
        assert f"/plant/{plant_id}/edit" in resp_upload.headers.get("Location", "")

        # Upload a second foto for hauptbild test
        _upload_foto(client, plant_id)
        fotos = db.get_fotos(plant_id)
        assert len(fotos) == 2

        # Set hauptbild → 302
        second_foto_id = fotos[1]["id"]
        resp_hauptbild = client.post(
            f"/foto/{second_foto_id}/hauptbild",
            follow_redirects=False,
        )
        assert resp_hauptbild.status_code == 302, (
            f"Expected 302 for hauptbild, got {resp_hauptbild.status_code}"
        )
        assert f"/plant/{plant_id}/edit" in resp_hauptbild.headers.get("Location", "")

        # Delete → 302
        resp_delete = client.post(
            f"/foto/{second_foto_id}/remove",
            follow_redirects=False,
        )
        assert resp_delete.status_code == 302, (
            f"Expected 302 for delete, got {resp_delete.status_code}"
        )
        assert f"/plant/{plant_id}/edit" in resp_delete.headers.get("Location", "")


# ---------------------------------------------------------------------------
# Property 4: Maximale Fotoanzahl pro Pflanze
# Feature: pflanzen-fotos, Property 4: Maximale Fotoanzahl pro Pflanze
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
)
def test_max_fotos_invariant(name, kategorie):
    """For any plant, uploading 6 fotos results in the first 5 succeeding
    and the 6th being rejected. The count in DB never exceeds 5.

    # Feature: pflanzen-fotos, Property 4: Maximale Fotoanzahl pro Pflanze

    **Validates: Requirements 3.1, 3.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()

        for i in range(6):
            resp = _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)
            count = db.count_fotos(plant_id)
            if i < 5:
                assert resp.status_code == 302, (
                    f"Upload {i+1} should succeed with 302, got {resp.status_code}"
                )
                assert count == i + 1, (
                    f"After upload {i+1}, expected {i+1} fotos, got {count}"
                )
            else:
                # 6th upload should be rejected (400)
                assert resp.status_code == 400, (
                    f"Upload 6 should be rejected with 400, got {resp.status_code}"
                )
                assert count == 5, (
                    f"After rejected upload 6, expected 5 fotos, got {count}"
                )

        # Final invariant check
        assert db.count_fotos(plant_id) <= 5


# ---------------------------------------------------------------------------
# Property 5: Foto-Anzeige auf der Bearbeitungsseite
# Feature: pflanzen-fotos, Property 5: Foto-Anzeige auf der Bearbeitungsseite
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    num_fotos=st.integers(min_value=0, max_value=5),
    bezeichnung=bezeichnung_st,
)
def test_foto_display_on_edit(name, kategorie, num_fotos, bezeichnung):
    """For any plant with 0-5 fotos, the edit page shows the correct number
    of foto images, bezeichnung appears in HTML, and hauptbild has class foto-hauptbild.

    # Feature: pflanzen-fotos, Property 5: Foto-Anzeige auf der Bearbeitungsseite

    **Validates: Requirements 4.1, 4.2, 11.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        for i in range(num_fotos):
            bez = bezeichnung if i == 0 else None
            _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes, bezeichnung=bez)

        resp = client.get(f"/plant/{plant_id}/edit")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")

        # Count foto images: <img src="/fotos/
        img_count = html.count('<img src="/fotos/')
        assert img_count == num_fotos, (
            f"Expected {num_fotos} foto images, found {img_count}"
        )

        # Check bezeichnung appears if set
        if num_fotos > 0 and bezeichnung and bezeichnung.strip():
            assert bezeichnung.strip() in html, (
                f"Expected bezeichnung '{bezeichnung.strip()}' in HTML"
            )

        # Check hauptbild class: first foto should be hauptbild
        if num_fotos > 0:
            assert "foto-hauptbild" in html, (
                "Expected 'foto-hauptbild' class for the hauptbild"
            )


# ---------------------------------------------------------------------------
# Property 6: Foto-Löschung entfernt DB-Eintrag und Datei
# Feature: pflanzen-fotos, Property 6: Foto-Löschung entfernt DB-Eintrag und Datei
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
)
def test_foto_delete_removes_db_and_file(name, kategorie):
    """For any existing foto, after deleting via POST /foto/<id>/remove,
    there is no DB entry and no file on disk for that foto.

    # Feature: pflanzen-fotos, Property 6: Foto-Löschung entfernt DB-Eintrag und Datei

    **Validates: Requirements 5.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)

        fotos = db.get_fotos(plant_id)
        assert len(fotos) == 1
        foto = fotos[0]
        foto_id = foto["id"]
        dateiname = foto["dateiname"]
        filepath = app_module.FOTOS_DIR / dateiname

        # File should exist before deletion
        assert filepath.exists(), f"Foto file should exist at {filepath}"

        # Delete the foto
        resp = client.post(f"/foto/{foto_id}/remove", follow_redirects=False)
        assert resp.status_code == 302

        # DB entry should be gone
        assert db.get_foto(foto_id) is None, "Foto DB entry should be deleted"

        # File should be gone
        assert not filepath.exists(), f"Foto file should be deleted at {filepath}"


# ---------------------------------------------------------------------------
# Property 7: Eindeutige Dateinamen
# Feature: pflanzen-fotos, Property 7: Eindeutige Dateinamen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    num_uploads=st.integers(min_value=2, max_value=5),
)
def test_unique_filenames(name, kategorie, num_uploads):
    """For any sequence of foto uploads, all dateiname values in DB are
    pairwise distinct.

    # Feature: pflanzen-fotos, Property 7: Eindeutige Dateinamen

    **Validates: Requirements 6.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        for _ in range(num_uploads):
            _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)

        fotos = db.get_fotos(plant_id)
        dateinamen = [f["dateiname"] for f in fotos]
        assert len(dateinamen) == len(set(dateinamen)), (
            f"Dateinamen are not unique: {dateinamen}"
        )


# ---------------------------------------------------------------------------
# Property 8: Pflanze löschen entfernt alle zugehörigen Fotos
# Feature: pflanzen-fotos, Property 8: Pflanze löschen entfernt alle zugehörigen Fotos
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    num_fotos=st.integers(min_value=1, max_value=5),
)
def test_plant_delete_removes_all_fotos(name, kategorie, num_fotos):
    """For any plant with 1-5 fotos, after deleting the plant via POST /remove/<id>,
    no foto files exist on disk and no foto DB entries remain.

    # Feature: pflanzen-fotos, Property 8: Pflanze löschen entfernt alle zugehörigen Fotos

    **Validates: Requirements 6.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        for _ in range(num_fotos):
            _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)

        fotos = db.get_fotos(plant_id)
        assert len(fotos) == num_fotos
        filepaths = [app_module.FOTOS_DIR / f["dateiname"] for f in fotos]

        # All files should exist before plant deletion
        for fp in filepaths:
            assert fp.exists(), f"Foto file should exist at {fp}"

        # Delete the plant
        resp = client.post(f"/remove/{plant_id}", follow_redirects=False)
        assert resp.status_code == 302

        # No foto files should remain
        for fp in filepaths:
            assert not fp.exists(), f"Foto file should be deleted at {fp}"

        # No DB entries should remain
        remaining = db.get_fotos(plant_id)
        assert len(remaining) == 0, (
            f"Expected 0 fotos after plant deletion, got {len(remaining)}"
        )


# ---------------------------------------------------------------------------
# Property 9: Nur gültige MIME-Typen werden akzeptiert
# Feature: pflanzen-fotos, Property 9: Nur gültige MIME-Typen werden akzeptiert
# ---------------------------------------------------------------------------

INVALID_MIME_TYPES = [
    "text/plain", "application/pdf", "image/gif", "image/bmp",
    "image/webp", "image/svg+xml", "application/octet-stream",
    "video/mp4", "audio/mpeg", "text/html",
]


@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    mime_type=st.sampled_from(INVALID_MIME_TYPES),
)
def test_invalid_mime_rejected(name, kategorie, mime_type):
    """For any file with an invalid MIME type, the upload is rejected
    with the error message 'Nur JPEG- und PNG-Dateien sind erlaubt.'

    # Feature: pflanzen-fotos, Property 9: Nur gültige MIME-Typen werden akzeptiert

    **Validates: Requirements 7.1, 7.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        # Create some random bytes as the file content
        file_bytes = b"not a real image content here"
        data = {
            "foto": (BytesIO(file_bytes), "test.dat"),
        }
        # We need to set the content_type on the file tuple for Flask
        # Use the werkzeug FileStorage approach via data dict
        resp = client.post(
            f"/plant/{plant_id}/foto/upload",
            data={"foto": (BytesIO(file_bytes), "test.dat", mime_type)},
            content_type="multipart/form-data",
            follow_redirects=True,
        )

        html = resp.data.decode("utf-8")
        assert "Nur JPEG- und PNG-Dateien sind erlaubt." in html, (
            f"Expected MIME rejection message for type '{mime_type}', not found in response"
        )

        # No foto should be in DB
        assert db.count_fotos(plant_id) == 0, (
            f"No foto should be stored for invalid MIME type '{mime_type}'"
        )


# ---------------------------------------------------------------------------
# Property 10: Hauptbild-Invariante — maximal ein Hauptbild pro Pflanze
# Feature: pflanzen-fotos, Property 10: Hauptbild-Invariante
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    num_fotos=st.integers(min_value=2, max_value=5),
    hauptbild_sequence=st.lists(st.integers(min_value=0, max_value=4), min_size=1, max_size=10),
)
def test_hauptbild_invariant(name, kategorie, num_fotos, hauptbild_sequence):
    """For any plant and any random sequence of hauptbild settings,
    at any point there is at most 1 foto with ist_hauptbild=1.

    # Feature: pflanzen-fotos, Property 10: Hauptbild-Invariante

    **Validates: Requirements 11.1, 11.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        for _ in range(num_fotos):
            _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)

        fotos = db.get_fotos(plant_id)
        foto_ids = [f["id"] for f in fotos]

        for idx in hauptbild_sequence:
            # Map index to valid foto id
            target_id = foto_ids[idx % len(foto_ids)]
            client.post(f"/foto/{target_id}/hauptbild", follow_redirects=False)

            # Check invariant: at most 1 hauptbild
            current_fotos = db.get_fotos(plant_id)
            hauptbild_count = sum(1 for f in current_fotos if f["ist_hauptbild"])
            assert hauptbild_count <= 1, (
                f"Expected at most 1 hauptbild, got {hauptbild_count} "
                f"after setting foto {target_id}"
            )


# ---------------------------------------------------------------------------
# Property 11: Erstes Foto wird automatisch Hauptbild
# Feature: pflanzen-fotos, Property 11: Erstes Foto wird automatisch Hauptbild
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
)
def test_first_foto_is_hauptbild(name, kategorie):
    """For any plant with no fotos, after uploading the first foto,
    that foto has ist_hauptbild=1.

    # Feature: pflanzen-fotos, Property 11: Erstes Foto wird automatisch Hauptbild

    **Validates: Requirements 11.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        # Verify no fotos exist
        assert db.count_fotos(plant_id) == 0

        jpeg_bytes = _make_jpeg_bytes()
        _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)

        fotos = db.get_fotos(plant_id)
        assert len(fotos) == 1, f"Expected 1 foto, got {len(fotos)}"
        assert fotos[0]["ist_hauptbild"] == 1, (
            f"First foto should be hauptbild, got ist_hauptbild={fotos[0]['ist_hauptbild']}"
        )


# ---------------------------------------------------------------------------
# Property 12: Kein automatisches Hauptbild nach Löschen
# Feature: pflanzen-fotos, Property 12: Kein automatisches Hauptbild nach Löschen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    kategorie=kategorie_st,
    num_fotos=st.integers(min_value=2, max_value=5),
)
def test_no_auto_hauptbild_after_delete(name, kategorie, num_fotos):
    """For any plant with >= 2 fotos, after deleting the hauptbild,
    no other foto has ist_hauptbild=1.

    # Feature: pflanzen-fotos, Property 12: Kein automatisches Hauptbild nach Löschen

    **Validates: Requirements 11.6**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)
        plant_id = _create_plant(db, name=name, kategorie=kategorie)

        app_module, client = _init_app(db_path)

        jpeg_bytes = _make_jpeg_bytes()
        for _ in range(num_fotos):
            _upload_foto(client, plant_id, jpeg_bytes=jpeg_bytes)

        fotos = db.get_fotos(plant_id)
        assert len(fotos) == num_fotos

        # Find the hauptbild (first foto should be hauptbild)
        hauptbild = [f for f in fotos if f["ist_hauptbild"]]
        assert len(hauptbild) == 1, f"Expected exactly 1 hauptbild, got {len(hauptbild)}"
        hauptbild_id = hauptbild[0]["id"]

        # Delete the hauptbild
        client.post(f"/foto/{hauptbild_id}/remove", follow_redirects=False)

        # Check: no other foto should have ist_hauptbild=1
        remaining_fotos = db.get_fotos(plant_id)
        assert len(remaining_fotos) == num_fotos - 1
        hauptbild_count = sum(1 for f in remaining_fotos if f["ist_hauptbild"])
        assert hauptbild_count == 0, (
            f"After deleting hauptbild, expected 0 hauptbilder, got {hauptbild_count}"
        )
