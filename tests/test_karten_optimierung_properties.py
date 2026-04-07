"""Property-based tests for the karten-optimierung feature (Hypothesis).

# Feature: karten-optimierung
"""
import importlib
import os
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

VALID_KATEGORIEN = ["Obst", "Gemüse", "Kräuter", "Stauden", "Gehölze", "Blumen", "Gründüngung", "Gartenpflege"]


def _init_db(db_path: str):
    """Initialise an isolated SQLite database and return the reloaded db module."""
    os.environ["DB_PATH"] = db_path
    import db as db_module
    importlib.reload(db_module)
    db_module.init_db()
    return db_module


def _add_plant(db_module, name="Testpflanze", kategorie="Gemüse", aktiv=1, farbe=None):
    """Add a minimal plant and return its id."""
    import sqlite3
    db_path = os.environ["DB_PATH"]
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.execute(
        "INSERT INTO plants (name, type, variety, lichtbedarf, kommentar, kategorie, farbe) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, "Gemüse", None, "Sonne", None, kategorie, farbe),
    )
    plant_id = cursor.lastrowid
    if aktiv == 0:
        conn.execute("UPDATE plants SET aktiv = 0 WHERE id = ?", (plant_id,))
    conn.commit()
    conn.close()
    return plant_id


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

plant_strategy = st.fixed_dictionaries({
    "name": st.text(
        alphabet=st.characters(whitelist_categories=("L", "N"), whitelist_characters=" -"),
        min_size=1, max_size=30,
    ),
    "kategorie": st.sampled_from(VALID_KATEGORIEN),
    "aktiv": st.sampled_from([0, 1]),
})


# ---------------------------------------------------------------------------
# Property 4: Erweiterte Abfrage liefert kategorie und aktiv
# Feature: karten-optimierung, Property 4: Erweiterte Abfrage liefert kategorie und aktiv
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    plants_data=st.lists(plant_strategy, min_size=1, max_size=5),
)
def test_get_kartenpositionen_returns_kategorie_and_aktiv(plants_data):
    """For any plant with a map position, get_kartenpositionen() returns
    kategorie and aktiv fields matching the original plant data.

    # Feature: karten-optimierung, Property 4: Erweiterte Abfrage liefert kategorie und aktiv

    **Validates: Requirements 5.1, 5.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)

        # Need a kartenbild for positions to make sense
        db_mod.save_kartenbild("dummy.jpg")

        # Create plants and positions, track expected data
        expected = {}  # plant_id -> {kategorie, aktiv}
        for i, pd in enumerate(plants_data):
            plant_id = _add_plant(
                db_mod,
                name=f"{pd['name']}_{i}",
                kategorie=pd["kategorie"],
                aktiv=pd["aktiv"],
            )
            x = round(10.0 + i * 15.0, 2)
            y = round(20.0 + i * 10.0, 2)
            db_mod.add_kartenposition(plant_id, x, y)
            expected[plant_id] = {
                "kategorie": pd["kategorie"],
                "aktiv": pd["aktiv"],
            }

        # Query positions
        positionen = db_mod.get_kartenpositionen()

        # Verify each position has kategorie and aktiv matching the plant
        assert len(positionen) == len(plants_data), (
            f"Expected {len(plants_data)} positions, got {len(positionen)}"
        )

        for pos in positionen:
            pid = pos["plant_id"]
            assert pid in expected, f"Unexpected plant_id {pid}"

            # Verify kategorie field exists and matches
            assert "kategorie" in pos, (
                f"Position for plant {pid} missing 'kategorie' field"
            )
            assert pos["kategorie"] == expected[pid]["kategorie"], (
                f"kategorie mismatch for plant {pid}: "
                f"got '{pos['kategorie']}', expected '{expected[pid]['kategorie']}'"
            )

            # Verify aktiv field exists and matches
            assert "aktiv" in pos, (
                f"Position for plant {pid} missing 'aktiv' field"
            )
            assert pos["aktiv"] == expected[pid]["aktiv"], (
                f"aktiv mismatch for plant {pid}: "
                f"got {pos['aktiv']}, expected {expected[pid]['aktiv']}"
            )


# ---------------------------------------------------------------------------
# Helpers for route-level tests
# ---------------------------------------------------------------------------

VALID_EREIGNISTYPEN = ["Blüte", "Ernte", "Düngen", "Rückschnitt", "Vorkultur", "Auspflanzen", "Direktsaat", "Pflege"]


def _get_test_client(db_path: str):
    """Reload app module with given DB_PATH and return the app module."""
    os.environ["DB_PATH"] = db_path
    import db as db_module
    importlib.reload(db_module)
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module


def _add_ereignis(db_module, plant_id, ereignistyp, startmonat, endmonat):
    """Add an event for a plant."""
    db_module.add_ereignis(plant_id, ereignistyp, startmonat, endmonat)


def _extract_marker_titles(html: str) -> set[str]:
    """Extract all marker title attributes from the rendered HTML."""
    import re
    return set(re.findall(r'class="karte-marker[^"]*"[^>]*title="([^"]*)"', html))


# ---------------------------------------------------------------------------
# Strategies for Property 1
# ---------------------------------------------------------------------------

active_plant_strategy = st.fixed_dictionaries({
    "name": st.text(
        alphabet=st.characters(whitelist_categories=("L",), whitelist_characters="-"),
        min_size=2, max_size=15,
    ),
    "kategorie": st.sampled_from(VALID_KATEGORIEN),
})

ereignis_strategy = st.fixed_dictionaries({
    "ereignistyp": st.sampled_from(VALID_EREIGNISTYPEN),
    "startmonat": st.integers(min_value=1, max_value=12),
    "endmonat": st.integers(min_value=1, max_value=12),
})


# ---------------------------------------------------------------------------
# Property 1: Filterung liefert nur passende Positionen
# Feature: karten-optimierung, Property 1: Filterung liefert nur passende Positionen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    plants_data=st.lists(active_plant_strategy, min_size=2, max_size=5),
    ereignisse_per_plant=st.lists(
        st.lists(ereignis_strategy, min_size=0, max_size=2),
        min_size=2, max_size=5,
    ),
    filter_kategorie=st.one_of(st.just(""), st.sampled_from(VALID_KATEGORIEN)),
    filter_ereignis=st.one_of(st.just(""), st.sampled_from(VALID_EREIGNISTYPEN)),
    filter_monat=st.one_of(st.just(""), st.integers(min_value=1, max_value=12).map(str)),
)
def test_filterung_liefert_nur_passende_positionen(
    plants_data, ereignisse_per_plant, filter_kategorie, filter_ereignis, filter_monat
):
    """For any combination of filter parameters and any set of plants with
    map positions and events: the filtered result SHALL only contain positions
    whose plant matches all active filters.

    # Feature: karten-optimierung, Property 1: Filterung liefert nur passende Positionen

    **Validates: Requirements 1.5, 1.6, 1.7, 1.8, 5.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Write a dummy kartenbild file so the template renders the map
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 20)
        db_mod.save_kartenbild("map.jpg")

        # Ensure ereignisse_per_plant matches plants_data length
        ereignisse_lists = ereignisse_per_plant[:len(plants_data)]
        while len(ereignisse_lists) < len(plants_data):
            ereignisse_lists.append([])

        # Create plants (all active), positions, and ereignisse
        # Use unique names by appending index
        plant_info = []  # list of (plant_id, unique_name, kategorie, [ereignisse])
        for i, pd in enumerate(plants_data):
            unique_name = f"{pd['name']}_{i}"
            plant_id = _add_plant(
                db_mod,
                name=unique_name,
                kategorie=pd["kategorie"],
                aktiv=1,
            )
            x = round(10.0 + i * 15.0, 2)
            y = round(20.0 + i * 10.0, 2)
            db_mod.add_kartenposition(plant_id, x, y)

            # Add ereignisse, ensuring startmonat <= endmonat
            plant_ereignisse = []
            for e_data in ereignisse_lists[i]:
                sm = min(e_data["startmonat"], e_data["endmonat"])
                em = max(e_data["startmonat"], e_data["endmonat"])
                _add_ereignis(db_mod, plant_id, e_data["ereignistyp"], sm, em)
                plant_ereignisse.append({
                    "ereignistyp": e_data["ereignistyp"],
                    "startmonat": sm,
                    "endmonat": em,
                })
            plant_info.append((plant_id, unique_name, pd["kategorie"], plant_ereignisse))

        # Build query params
        params = {}
        if filter_kategorie:
            params["kategorie"] = filter_kategorie
        if filter_ereignis:
            params["ereignis"] = filter_ereignis
        if filter_monat:
            params["monat"] = filter_monat

        # Make request
        with app_module.app.test_client() as client:
            resp = client.get("/gartenkarte", query_string=params)
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

        shown_names = _extract_marker_titles(html)

        # Compute expected set of names that should pass all filters
        expected_names = set()
        for plant_id, name, kategorie, ereignisse in plant_info:
            # Check kategorie filter
            if filter_kategorie and kategorie != filter_kategorie:
                continue

            # Check ereignis/monat filter
            if filter_ereignis or filter_monat:
                matching_ereignisse = ereignisse
                if filter_ereignis:
                    matching_ereignisse = [
                        e for e in matching_ereignisse
                        if e["ereignistyp"] == filter_ereignis
                    ]
                if filter_monat:
                    try:
                        fm = int(filter_monat)
                    except ValueError:
                        fm = None
                    if fm and 1 <= fm <= 12:
                        matching_ereignisse = [
                            e for e in matching_ereignisse
                            if e["startmonat"] <= fm <= e["endmonat"]
                        ]
                if not matching_ereignisse:
                    continue

            expected_names.add(name)

        assert shown_names == expected_names, (
            f"Filter(kategorie={filter_kategorie!r}, ereignis={filter_ereignis!r}, "
            f"monat={filter_monat!r})\n"
            f"Expected names: {sorted(expected_names)}\n"
            f"Shown names:    {sorted(shown_names)}"
        )


# ---------------------------------------------------------------------------
# Property 5: Nur aktive Pflanzen auf der Karte
# Feature: karten-optimierung, Property 5: Nur aktive Pflanzen auf der Karte
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    plants_data=st.lists(plant_strategy, min_size=1, max_size=6),
)
def test_nur_aktive_pflanzen_auf_der_karte(plants_data):
    """For any set of plants (active and inactive) with map positions,
    the garden map SHALL only display markers for active plants (aktiv=1).

    # Feature: karten-optimierung, Property 5: Nur aktive Pflanzen auf der Karte

    **Validates: Requirements 5.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Write a dummy kartenbild file so the template renders the map
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 20)
        db_mod.save_kartenbild("map.jpg")

        # Create plants with mixed aktiv status and positions for all
        expected_active_names = set()
        all_names = set()
        for i, pd in enumerate(plants_data):
            unique_name = f"{pd['name']}_{i}"
            plant_id = _add_plant(
                db_mod,
                name=unique_name,
                kategorie=pd["kategorie"],
                aktiv=pd["aktiv"],
            )
            x = round(5.0 + i * 12.0, 2)
            y = round(10.0 + i * 8.0, 2)
            db_mod.add_kartenposition(plant_id, x, y)
            all_names.add(unique_name)
            if pd["aktiv"] == 1:
                expected_active_names.add(unique_name)

        # Request the map page without any filters
        with app_module.app.test_client() as client:
            resp = client.get("/gartenkarte")
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

        shown_names = _extract_marker_titles(html)
        inactive_names = all_names - expected_active_names

        # Only active plants should appear as markers
        assert shown_names == expected_active_names, (
            f"Expected only active plant markers.\n"
            f"Shown:    {sorted(shown_names)}\n"
            f"Expected: {sorted(expected_active_names)}\n"
            f"Inactive (should NOT appear): {sorted(inactive_names)}"
        )

        # Explicitly verify no inactive plant appears
        for name in inactive_names:
            assert name not in shown_names, (
                f"Inactive plant '{name}' should not appear on the map"
            )


# ---------------------------------------------------------------------------
# Property 2: Kategoriespezifische Marker-Klassen
# Feature: karten-optimierung, Property 2: Kategoriespezifische Marker-Klassen
# ---------------------------------------------------------------------------

import re


@settings(max_examples=100, deadline=None)
@given(
    plants_data=st.lists(
        st.fixed_dictionaries({
            "name": st.text(
                alphabet=st.characters(whitelist_categories=("L",), whitelist_characters="-"),
                min_size=2, max_size=15,
            ),
            "kategorie": st.sampled_from(VALID_KATEGORIEN),
            "x": st.floats(min_value=5.0, max_value=95.0, allow_nan=False, allow_infinity=False),
            "y": st.floats(min_value=5.0, max_value=95.0, allow_nan=False, allow_infinity=False),
        }),
        min_size=1,
        max_size=6,
    ),
)
def test_kategoriespezifische_marker_klassen(plants_data):
    """For any active plant with a map position: if kategorie is 'Gehölze',
    the marker SHALL have class 'karte-marker-gehoelz'; if 'Gartenpflege',
    it SHALL have class 'karte-marker-gartenpflege'; for all other categories,
    neither extra class SHALL be present.

    # Feature: karten-optimierung, Property 2: Kategoriespezifische Marker-Klassen

    **Validates: Requirements 2.1, 2.3, 3.1, 3.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Write a dummy kartenbild file
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 20)
        db_mod.save_kartenbild("map.jpg")

        # Create active plants with positions, track expected kategorie per plant_id
        expected = {}  # plant_id -> kategorie
        for i, pd in enumerate(plants_data):
            unique_name = f"{pd['name']}_{i}"
            plant_id = _add_plant(
                db_mod,
                name=unique_name,
                kategorie=pd["kategorie"],
                aktiv=1,
            )
            x = round(pd["x"], 2)
            y = round(pd["y"], 2)
            db_mod.add_kartenposition(plant_id, x, y)
            expected[plant_id] = pd["kategorie"]

        # Request the map page
        with app_module.app.test_client() as client:
            resp = client.get("/gartenkarte")
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

        # Extract all marker divs: capture class attribute and data-plant-id
        # Pattern matches: class="karte-marker..." ... data-plant-id="123"
        marker_pattern = re.compile(
            r'<div\s+class="([^"]*karte-marker[^"]*)"[^>]*data-plant-id="(\d+)"'
        )
        markers = marker_pattern.findall(html)

        # We should have one marker per plant
        found_ids = {int(pid) for _, pid in markers}
        assert found_ids == set(expected.keys()), (
            f"Expected markers for plant_ids {sorted(expected.keys())}, "
            f"found {sorted(found_ids)}"
        )

        for class_attr, plant_id_str in markers:
            plant_id = int(plant_id_str)
            kategorie = expected[plant_id]

            if kategorie == "Gehölze":
                assert "karte-marker-gehoelz" in class_attr, (
                    f"Plant {plant_id} (kategorie='Gehölze') should have "
                    f"'karte-marker-gehoelz' in classes, got: '{class_attr}'"
                )
                assert "karte-marker-gartenpflege" not in class_attr, (
                    f"Plant {plant_id} (kategorie='Gehölze') should NOT have "
                    f"'karte-marker-gartenpflege', got: '{class_attr}'"
                )
            elif kategorie == "Gartenpflege":
                assert "karte-marker-gartenpflege" in class_attr, (
                    f"Plant {plant_id} (kategorie='Gartenpflege') should have "
                    f"'karte-marker-gartenpflege' in classes, got: '{class_attr}'"
                )
                assert "karte-marker-gehoelz" not in class_attr, (
                    f"Plant {plant_id} (kategorie='Gartenpflege') should NOT have "
                    f"'karte-marker-gehoelz', got: '{class_attr}'"
                )
            else:
                assert "karte-marker-gehoelz" not in class_attr, (
                    f"Plant {plant_id} (kategorie='{kategorie}') should NOT have "
                    f"'karte-marker-gehoelz', got: '{class_attr}'"
                )
                assert "karte-marker-gartenpflege" not in class_attr, (
                    f"Plant {plant_id} (kategorie='{kategorie}') should NOT have "
                    f"'karte-marker-gartenpflege', got: '{class_attr}'"
                )


# ---------------------------------------------------------------------------
# Property 3: data-plant-id Attribut auf Markierungen
# Feature: karten-optimierung, Property 3: data-plant-id Attribut auf Markierungen
# ---------------------------------------------------------------------------


@settings(max_examples=100, deadline=None)
@given(
    plants_data=st.lists(
        st.fixed_dictionaries({
            "name": st.text(
                alphabet=st.characters(whitelist_categories=("L",), whitelist_characters="-"),
                min_size=2, max_size=15,
            ),
            "kategorie": st.sampled_from(VALID_KATEGORIEN),
            "x": st.floats(min_value=5.0, max_value=95.0, allow_nan=False, allow_infinity=False),
            "y": st.floats(min_value=5.0, max_value=95.0, allow_nan=False, allow_infinity=False),
        }),
        min_size=1,
        max_size=6,
    ),
)
def test_data_plant_id_attribut_auf_markierungen(plants_data):
    """For any active plant with a map position, the rendered marker SHALL
    have a data-plant-id attribute whose value matches the plant_id of the
    position.

    # Feature: karten-optimierung, Property 3: data-plant-id Attribut auf Markierungen

    **Validates: Requirements 4.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)
        karte_dir = os.path.join(tmp_dir, "karte")
        os.makedirs(karte_dir, exist_ok=True)
        app_module.KARTE_DIR = __import__("pathlib").Path(karte_dir)

        # Write a dummy kartenbild file
        import pathlib
        (pathlib.Path(karte_dir) / "map.jpg").write_bytes(b"\xff\xd8\xff\xe0" + b"\x00" * 20)
        db_mod.save_kartenbild("map.jpg")

        # Create active plants with positions, track expected plant_ids
        expected_ids = set()
        for i, pd in enumerate(plants_data):
            unique_name = f"{pd['name']}_{i}"
            plant_id = _add_plant(
                db_mod,
                name=unique_name,
                kategorie=pd["kategorie"],
                aktiv=1,
            )
            x = round(pd["x"], 2)
            y = round(pd["y"], 2)
            db_mod.add_kartenposition(plant_id, x, y)
            expected_ids.add(plant_id)

        # Request the map page
        with app_module.app.test_client() as client:
            resp = client.get("/gartenkarte")
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

        # Extract all marker divs: capture class attribute and data-plant-id
        marker_pattern = re.compile(
            r'<div\s+class="([^"]*karte-marker[^"]*)"[^>]*data-plant-id="(\d+)"'
        )
        markers = marker_pattern.findall(html)

        # Every expected plant_id must appear as a marker with data-plant-id
        found_ids = {int(pid) for _, pid in markers}
        assert found_ids == expected_ids, (
            f"Expected data-plant-id values {sorted(expected_ids)}, "
            f"found {sorted(found_ids)}"
        )

        # Each marker must have a valid data-plant-id matching one of our plants
        for class_attr, plant_id_str in markers:
            plant_id = int(plant_id_str)
            assert plant_id in expected_ids, (
                f"Marker has data-plant-id={plant_id} which is not in "
                f"expected plant ids {sorted(expected_ids)}"
            )
