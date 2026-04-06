"""Property-based tests for the gartenkarte feature (Hypothesis).

# Feature: gartenkarte
"""
import importlib
import os
import sqlite3
import tempfile
from io import BytesIO

import pytest
from hypothesis import given, settings, assume
from hypothesis import strategies as st
from PIL import Image


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


def _make_image_bytes(width: int, height: int, fmt: str = "JPEG") -> bytes:
    """Create a minimal in-memory image and return its bytes."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = BytesIO()
    img.save(buf, format=fmt, quality=85)
    return buf.getvalue()


def _get_test_client(db_path: str):
    """Reload app module with given DB_PATH and return a Flask test client context."""
    os.environ["DB_PATH"] = db_path
    import db as db_module
    importlib.reload(db_module)
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module


def _add_plant(db_module, name="Testpflanze", farbe=None):
    """Add a minimal plant and return its id."""
    db_module.add_plant(
        name=name, type="Gemüse", variety=None,
        lichtbedarf="Sonne", kommentar=None, kategorie="Gemüse",
        farbe=farbe,
    )
    plants = db_module.get_all_plants(include_inactive=True)
    return plants[-1]["id"]



# ---------------------------------------------------------------------------
# Property 1: Bildverkleinerung und JPEG-Konvertierung
# Feature: gartenkarte, Property 1: Bildverkleinerung und JPEG-Konvertierung
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    width=st.integers(min_value=1, max_value=5000),
    height=st.integers(min_value=1, max_value=5000),
)
def test_kartenbild_resize_and_jpeg(width, height):
    """For any image with random dimensions, after process_kartenbild():
    result is JPEG, long side = min(original, 1920), aspect ratio preserved.

    # Feature: gartenkarte, Property 1: Bildverkleinerung und JPEG-Konvertierung

    **Validates: Requirements 2.1, 2.2, 2.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        _init_db(db_path)
        app_module = _get_test_client(db_path)

        # Create source image
        img_bytes = _make_image_bytes(width, height)
        file_obj = BytesIO(img_bytes)

        result_bytes = app_module.process_kartenbild(file_obj)

        # Verify output is JPEG
        result_img = Image.open(BytesIO(result_bytes))
        assert result_img.format == "JPEG", f"Expected JPEG, got {result_img.format}"

        # Verify dimensions
        orig_long = max(width, height)
        expected_long = min(orig_long, 1920)
        result_long = max(result_img.size)

        assert result_long == expected_long, (
            f"Expected long side {expected_long}, got {result_long} "
            f"(original {width}x{height})"
        )

        # Verify aspect ratio preserved proportionally.
        # PIL thumbnail uses integer rounding, so for very extreme ratios
        # (e.g. 5000x1) the short side may round to 0→1. We check that
        # the result matches what PIL.Image.thumbnail would produce.
        if orig_long > 1920:
            # Thumbnail was applied — verify PIL's own rounding is respected
            ref = Image.new("RGB", (width, height))
            ref.thumbnail((1920, 1920), Image.LANCZOS)
            assert result_img.size == ref.size, (
                f"Size mismatch: got {result_img.size}, expected {ref.size} "
                f"(original {width}x{height})"
            )
        else:
            # No resize — dimensions should be unchanged
            assert result_img.size == (width, height)


# ---------------------------------------------------------------------------
# Property 2: Upload speichert Kartenbild korrekt
# Feature: gartenkarte, Property 2: Upload speichert Kartenbild korrekt
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    width=st.integers(min_value=10, max_value=500),
    height=st.integers(min_value=10, max_value=500),
)
def test_upload_stores_kartenbild(width, height):
    """For any valid image, after upload: exactly one file in karte/ dir
    and exactly one DB entry with matching filename.

    # Feature: gartenkarte, Property 2: Upload speichert Kartenbild korrekt

    **Validates: Requirements 1.2, 8.1**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        img_bytes = _make_image_bytes(width, height)

        with app_module.app.test_client() as client:
            resp = client.post(
                "/gartenkarte/bild/upload",
                data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                content_type="multipart/form-data",
                follow_redirects=False,
            )
            assert resp.status_code == 302

        # Verify exactly one file in karte/
        files = os.listdir(karte_dir)
        assert len(files) == 1, f"Expected 1 file in karte/, got {len(files)}: {files}"

        # Verify DB entry matches
        import db as db_module
        importlib.reload(db_module)
        kb = db_module.get_kartenbild()
        assert kb is not None, "Expected kartenbild DB entry"
        assert kb["dateiname"] == files[0], (
            f"DB dateiname '{kb['dateiname']}' != file '{files[0]}'"
        )



# ---------------------------------------------------------------------------
# Property 3: Nur gültige MIME-Typen werden akzeptiert
# Feature: gartenkarte, Property 3: Nur gültige MIME-Typen werden akzeptiert
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    mime_type=st.text(
        alphabet=st.characters(whitelist_categories=("L", "N", "P", "S"),
                               blacklist_characters="\r\n"),
        min_size=1,
        max_size=50,
    ).filter(lambda s: s not in {"image/jpeg", "image/png"}),
)
def test_invalid_mime_rejected(mime_type):
    """For any invalid MIME type, upload is rejected with the correct error message.

    # Feature: gartenkarte, Property 3: Nur gültige MIME-Typen werden akzeptiert

    **Validates: Requirements 1.4, 1.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Use valid image bytes but wrong MIME type
        img_bytes = _make_image_bytes(100, 100)

        with app_module.app.test_client() as client:
            resp = client.post(
                "/gartenkarte/bild/upload",
                data={"bild": (BytesIO(img_bytes), "test.dat", mime_type)},
                content_type="multipart/form-data",
            )
            assert resp.status_code == 400
            html = resp.data.decode("utf-8")
            assert "Nur JPEG- und PNG-Dateien sind erlaubt." in html


# ---------------------------------------------------------------------------
# Property 4: Kartenbild ersetzen löscht alte Datei
# Feature: gartenkarte, Property 4: Kartenbild ersetzen löscht alte Datei
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    w1=st.integers(min_value=10, max_value=200),
    h1=st.integers(min_value=10, max_value=200),
    w2=st.integers(min_value=10, max_value=200),
    h2=st.integers(min_value=10, max_value=200),
)
def test_replace_deletes_old_file(w1, h1, w2, h2):
    """Two uploads in sequence: old file deleted, new file present, exactly one DB entry.

    # Feature: gartenkarte, Property 4: Kartenbild ersetzen löscht alte Datei

    **Validates: Requirements 3.2, 8.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        img1 = _make_image_bytes(w1, h1)
        img2 = _make_image_bytes(w2, h2)

        with app_module.app.test_client() as client:
            # First upload
            client.post(
                "/gartenkarte/bild/upload",
                data={"bild": (BytesIO(img1), "first.jpg", "image/jpeg")},
                content_type="multipart/form-data",
            )
            files_after_first = set(os.listdir(karte_dir))
            assert len(files_after_first) == 1

            # Second upload
            client.post(
                "/gartenkarte/bild/upload",
                data={"bild": (BytesIO(img2), "second.jpg", "image/jpeg")},
                content_type="multipart/form-data",
            )

        files_after_second = set(os.listdir(karte_dir))
        assert len(files_after_second) == 1, (
            f"Expected 1 file after replace, got {len(files_after_second)}"
        )
        # Old file should be gone
        assert files_after_first != files_after_second, "Old file was not replaced"

        # Exactly one DB entry
        import db as db_module
        importlib.reload(db_module)
        kb = db_module.get_kartenbild()
        assert kb is not None
        assert kb["dateiname"] in files_after_second



# ---------------------------------------------------------------------------
# Property 5: Kartenbild löschen entfernt Bild und alle Positionen
# Feature: gartenkarte, Property 5: Kartenbild löschen entfernt Bild und alle Positionen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    num_positions=st.integers(min_value=0, max_value=5),
)
def test_delete_removes_image_and_positions(num_positions):
    """Upload kartenbild, add 0-N positions, then delete: no file, no DB entries.

    # Feature: gartenkarte, Property 5: Kartenbild löschen entfernt Bild und alle Positionen

    **Validates: Requirements 3.4, 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Add a plant for positions
        plant_id = _add_plant(db_mod)

        with app_module.app.test_client() as client:
            # Upload kartenbild
            img_bytes = _make_image_bytes(100, 100)
            client.post(
                "/gartenkarte/bild/upload",
                data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                content_type="multipart/form-data",
            )

            # Add positions
            for i in range(num_positions):
                x = round(10.0 + i * 15.0, 2)
                y = round(20.0 + i * 10.0, 2)
                client.post(
                    "/gartenkarte/position/add",
                    data={"plant_id": str(plant_id), "x": str(x), "y": str(y)},
                )

            # Delete kartenbild
            client.post("/gartenkarte/bild/remove")

        # Verify no files
        files = os.listdir(karte_dir)
        assert len(files) == 0, f"Expected 0 files after delete, got {len(files)}"

        # Verify no DB entries
        importlib.reload(db_mod)
        assert db_mod.get_kartenbild() is None
        assert len(db_mod.get_kartenpositionen()) == 0


# ---------------------------------------------------------------------------
# Property 6: Position speichern mit korrekten Koordinaten
# Feature: gartenkarte, Property 6: Position speichern mit korrekten Koordinaten
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    x=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    y=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_position_stored_correctly(x, y):
    """Random valid coordinates are correctly stored in DB with matching plant_id.

    # Feature: gartenkarte, Property 6: Position speichern mit korrekten Koordinaten

    **Validates: Requirements 4.3, 4.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)

        plant_id = _add_plant(db_mod)

        # We need a kartenbild for the route to accept positions
        db_mod.save_kartenbild("dummy.jpg")

        db_mod.add_kartenposition(plant_id, x, y)

        positionen = db_mod.get_kartenpositionen()
        assert len(positionen) == 1
        pos = positionen[0]
        assert pos["plant_id"] == plant_id
        assert abs(pos["x"] - x) < 1e-9, f"x mismatch: {pos['x']} != {x}"
        assert abs(pos["y"] - y) < 1e-9, f"y mismatch: {pos['y']} != {y}"



# ---------------------------------------------------------------------------
# Property 7: Markierungen korrekt gerendert
# Feature: gartenkarte, Property 7: Markierungen korrekt gerendert
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    positions=st.lists(
        st.tuples(
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            st.one_of(st.none(), st.just("#ff0000"), st.just("#00ff00"), st.just("#0000ff")),
        ),
        min_size=1,
        max_size=5,
    ),
)
def test_markers_rendered_correctly(positions):
    """Random positions with plant data: HTML contains markers with correct
    left:x%;top:y%, title attribute, and optionally background:farbe.

    # Feature: gartenkarte, Property 7: Markierungen korrekt gerendert

    **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Upload a kartenbild (write file directly to avoid route overhead)
        img_bytes = _make_image_bytes(100, 100)
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(img_bytes)
        db_mod.save_kartenbild("map.jpg")

        # Add plants and positions
        plant_data = []
        for i, (x, y, farbe) in enumerate(positions):
            name = f"Pflanze_{i}"
            pid = _add_plant(db_mod, name=name, farbe=farbe)
            db_mod.add_kartenposition(pid, x, y)
            plant_data.append((name, x, y, farbe))

        with app_module.app.test_client() as client:
            resp = client.get("/gartenkarte")
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

        for name, x, y, farbe in plant_data:
            # Check position in style attribute
            x_str = f"left:{x}%"
            y_str = f"top:{y}%"
            assert x_str in html, f"Missing '{x_str}' in HTML for {name}"
            assert y_str in html, f"Missing '{y_str}' in HTML for {name}"

            # Check title attribute
            assert f'title="{name}"' in html, f"Missing title for {name}"

            # Check farbe if present
            if farbe:
                assert f"background:{farbe}" in html, (
                    f"Missing background:{farbe} for {name}"
                )


# ---------------------------------------------------------------------------
# Property 8: Position entfernen löscht DB-Eintrag
# Feature: gartenkarte, Property 8: Position entfernen löscht DB-Eintrag
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    x=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
    y=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
)
def test_position_remove_deletes_entry(x, y):
    """Random existing position: after removal, no DB entry with that ID.

    # Feature: gartenkarte, Property 8: Position entfernen löscht DB-Eintrag

    **Validates: Requirements 6.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Setup: kartenbild + plant + position
        img_bytes = _make_image_bytes(50, 50)
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(img_bytes)
        db_mod.save_kartenbild("map.jpg")
        plant_id = _add_plant(db_mod)
        db_mod.add_kartenposition(plant_id, x, y)

        positionen = db_mod.get_kartenpositionen()
        assert len(positionen) == 1
        pos_id = positionen[0]["id"]

        with app_module.app.test_client() as client:
            resp = client.post(f"/gartenkarte/position/{pos_id}/remove",
                               follow_redirects=False)
            assert resp.status_code == 302

        # Reload and verify
        importlib.reload(db_mod)
        remaining = db_mod.get_kartenpositionen()
        assert all(p["id"] != pos_id for p in remaining), (
            f"Position {pos_id} still exists after removal"
        )



# ---------------------------------------------------------------------------
# Property 9: Pflanze löschen entfernt alle zugehörigen Kartenpositionen
# Feature: gartenkarte, Property 9: Pflanze löschen entfernt alle zugehörigen Kartenpositionen
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    num_positions=st.integers(min_value=0, max_value=5),
)
def test_plant_delete_cascades_positions(num_positions):
    """Plant with 0-N map positions: after deleting plant, no entries with
    that plant_id in kartenpositionen (ON DELETE CASCADE).

    # Feature: gartenkarte, Property 9: Pflanze löschen entfernt alle zugehörigen Kartenpositionen

    **Validates: Requirements 6.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)

        plant_id = _add_plant(db_mod)
        db_mod.save_kartenbild("dummy.jpg")

        for i in range(num_positions):
            db_mod.add_kartenposition(plant_id, float(i * 10), float(i * 10))

        # Verify positions exist
        before = db_mod.get_kartenpositionen()
        assert len(before) == num_positions

        # Delete the plant
        db_mod.remove_plant(plant_id)

        # Verify no positions remain for that plant
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM kartenpositionen WHERE plant_id = ?", (plant_id,)
        ).fetchall()
        conn.close()
        assert len(rows) == 0, (
            f"Expected 0 positions for deleted plant, got {len(rows)}"
        )


# ---------------------------------------------------------------------------
# Property 10: Maximal ein Kartenbild-Eintrag
# Feature: gartenkarte, Property 10: Maximal ein Kartenbild-Eintrag
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    ops=st.lists(
        st.sampled_from(["upload", "delete"]),
        min_size=1,
        max_size=10,
    ),
)
def test_max_one_kartenbild_row(ops):
    """Random sequence of upload and delete operations: kartenbild table
    always has max 1 row.

    # Feature: gartenkarte, Property 10: Maximal ein Kartenbild-Eintrag

    **Validates: Requirements 7.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        img_bytes = _make_image_bytes(50, 50)

        with app_module.app.test_client() as client:
            for op in ops:
                if op == "upload":
                    client.post(
                        "/gartenkarte/bild/upload",
                        data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                        content_type="multipart/form-data",
                    )
                else:
                    client.post("/gartenkarte/bild/remove")

                # After each operation, check invariant
                conn = sqlite3.connect(db_path)
                count = conn.execute("SELECT COUNT(*) FROM kartenbild").fetchone()[0]
                conn.close()
                assert count <= 1, (
                    f"kartenbild has {count} rows after '{op}' (max 1 allowed)"
                )


# ---------------------------------------------------------------------------
# Property 11: Ungültige Koordinaten werden abgelehnt
# Feature: gartenkarte, Property 11: Ungültige Koordinaten werden abgelehnt
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    x=st.floats(allow_nan=False, allow_infinity=False).filter(
        lambda f: f < 0.0 or f > 100.0
    ),
    y=st.floats(allow_nan=False, allow_infinity=False).filter(
        lambda f: f < 0.0 or f > 100.0
    ),
)
def test_invalid_coordinates_rejected(x, y):
    """Random coordinates outside [0.0, 100.0]: request rejected with
    'Ungültige Koordinaten.'

    # Feature: gartenkarte, Property 11: Ungültige Koordinaten werden abgelehnt

    **Validates: Requirements 11.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Setup: kartenbild + plant
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(_make_image_bytes(50, 50))
        db_mod.save_kartenbild("map.jpg")
        plant_id = _add_plant(db_mod)

        with app_module.app.test_client() as client:
            resp = client.post(
                "/gartenkarte/position/add",
                data={"plant_id": str(plant_id), "x": str(x), "y": str(y)},
            )
            assert resp.status_code == 400
            html = resp.data.decode("utf-8")
            assert "Ungültige Koordinaten." in html



# ---------------------------------------------------------------------------
# Property 12: Redirect nach Karten-Operationen
# Feature: gartenkarte, Property 12: Redirect nach Karten-Operationen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    op=st.sampled_from(["upload", "delete", "position_add", "position_remove"]),
)
def test_redirect_after_karte_ops(op):
    """Successful karte operations return HTTP 302 redirect to /gartenkarte.

    # Feature: gartenkarte, Property 12: Redirect nach Karten-Operationen

    **Validates: Requirements 1.3, 6.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        img_bytes = _make_image_bytes(50, 50)
        plant_id = _add_plant(db_mod)

        with app_module.app.test_client() as client:
            if op == "upload":
                resp = client.post(
                    "/gartenkarte/bild/upload",
                    data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                    content_type="multipart/form-data",
                    follow_redirects=False,
                )
            elif op == "delete":
                # First upload so there's something to delete
                client.post(
                    "/gartenkarte/bild/upload",
                    data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                    content_type="multipart/form-data",
                )
                resp = client.post("/gartenkarte/bild/remove",
                                   follow_redirects=False)
            elif op == "position_add":
                # Need kartenbild first
                client.post(
                    "/gartenkarte/bild/upload",
                    data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                    content_type="multipart/form-data",
                )
                resp = client.post(
                    "/gartenkarte/position/add",
                    data={"plant_id": str(plant_id), "x": "50.0", "y": "50.0"},
                    follow_redirects=False,
                )
            elif op == "position_remove":
                # Need kartenbild + position first
                client.post(
                    "/gartenkarte/bild/upload",
                    data={"bild": (BytesIO(img_bytes), "test.jpg", "image/jpeg")},
                    content_type="multipart/form-data",
                )
                client.post(
                    "/gartenkarte/position/add",
                    data={"plant_id": str(plant_id), "x": "50.0", "y": "50.0"},
                )
                # Get position id
                importlib.reload(db_mod)
                positionen = db_mod.get_kartenpositionen()
                pos_id = positionen[0]["id"]
                resp = client.post(
                    f"/gartenkarte/position/{pos_id}/remove",
                    follow_redirects=False,
                )

            assert resp.status_code == 302, (
                f"Expected 302 for '{op}', got {resp.status_code}"
            )
            location = resp.headers.get("Location", "")
            assert location.endswith("/gartenkarte"), (
                f"Expected redirect to /gartenkarte for '{op}', got '{location}'"
            )
