"""Property-based tests for the ui-konsistenz-verbesserungen feature (Hypothesis).

# Feature: ui-konsistenz-verbesserungen
"""
import importlib
import os
import tempfile

from hypothesis import given, settings
from hypothesis import strategies as st


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


# Strategy: optional hex color or None
_farbe_strategy = st.one_of(
    st.none(),
    st.from_regex(r"#[0-9a-fA-F]{6}", fullmatch=True),
)

# Valid event types used in the project
_VALID_EREIGNISTYPEN = [
    "Blüte", "Ernte", "Düngen", "Rückschnitt",
    "Vorkultur", "Auspflanzen", "Direktsaat", "Pflege",
]


# ---------------------------------------------------------------------------
# Property 1: Farbe-Feld in Beobachtungen und Ereignissen
# Feature: ui-konsistenz-verbesserungen, Property 1: Farbe-Feld in Beobachtungen und Ereignissen
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    farbe=_farbe_strategy,
    ereignistyp=st.sampled_from(_VALID_EREIGNISTYPEN),
    monat=st.integers(min_value=1, max_value=12),
    jahr=st.integers(min_value=2000, max_value=2099),
)
def test_farbe_feld_in_beobachtungen_und_ereignissen(farbe, ereignistyp, monat, jahr):
    """For any plant with or without a color, get_all_beobachtungen() and
    get_all_ereignisse() return a 'farbe' field matching the plant's color.

    # Feature: ui-konsistenz-verbesserungen, Property 1: Farbe-Feld in Beobachtungen und Ereignissen

    **Validates: Requirements 1.1, 1.2, 1.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)

        # Create a plant with the generated farbe
        db_mod.add_plant(
            name="Testpflanze",
            type="Gemüse",
            variety=None,
            lichtbedarf="Sonne",
            kommentar=None,
            kategorie="Gemüse",
            farbe=farbe,
        )
        plants = db_mod.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Add a beobachtung for this plant
        db_mod.add_beobachtung(
            plant_id=plant_id,
            jahr=jahr,
            ereignistyp=ereignistyp,
            startmonat=monat,
            endmonat=monat,
        )

        # Add an ereignis for this plant
        db_mod.add_ereignis(
            plant_id=plant_id,
            ereignistyp=ereignistyp,
            startmonat=monat,
            endmonat=monat,
        )

        # Query and verify beobachtungen
        beobachtungen = db_mod.get_all_beobachtungen()
        assert len(beobachtungen) >= 1, "Expected at least one beobachtung"
        matching_b = [b for b in beobachtungen if b["plant_id"] == plant_id]
        assert len(matching_b) == 1, f"Expected 1 beobachtung for plant, got {len(matching_b)}"
        assert "farbe" in matching_b[0], "Beobachtung result missing 'farbe' field"
        assert matching_b[0]["farbe"] == farbe, (
            f"Beobachtung farbe mismatch: expected {farbe!r}, got {matching_b[0]['farbe']!r}"
        )

        # Query and verify ereignisse
        ereignisse = db_mod.get_all_ereignisse()
        assert len(ereignisse) >= 1, "Expected at least one ereignis"
        matching_e = [e for e in ereignisse if e["plant_id"] == plant_id]
        assert len(matching_e) == 1, f"Expected 1 ereignis for plant, got {len(matching_e)}"
        assert "farbe" in matching_e[0], "Ereignis result missing 'farbe' field"
        assert matching_e[0]["farbe"] == farbe, (
            f"Ereignis farbe mismatch: expected {farbe!r}, got {matching_e[0]['farbe']!r}"
        )


# ---------------------------------------------------------------------------
# Helpers for Flask test client
# ---------------------------------------------------------------------------

def _get_test_client(db_path: str):
    """Reload app module with given DB_PATH and return the reloaded app module."""
    os.environ["DB_PATH"] = db_path
    import db as db_module
    importlib.reload(db_module)
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    return app_module


def _add_plant(db_path, name="Testpflanze", farbe=None, aktiv=True):
    """Add a plant and optionally deactivate it. Returns its id."""
    import db as db_module
    db_module.add_plant(
        name=name, type="Gemüse", variety=None,
        lichtbedarf="Sonne", kommentar=None, kategorie="Gemüse",
        farbe=farbe,
    )
    plants = db_module.get_all_plants(include_inactive=True)
    # Find by name (get_all_plants sorts by name, so [-1] is unreliable)
    plant_id = next(p["id"] for p in plants if p["name"] == name)
    if not aktiv:
        db_module.set_plant_active(plant_id, 0)
    return plant_id


# Strategy: plant entry with a unique prefix to avoid collisions with other HTML text
_plant_entry = st.fixed_dictionaries({
    "name": st.text(
        alphabet="abcdefghijklmnopqrstuvwxyz",
        min_size=2,
        max_size=15,
    ).map(lambda s: "PBT_" + s),
    "aktiv": st.booleans(),
})


# ---------------------------------------------------------------------------
# Property 2: Nur aktive Pflanzen im Ereignis-Dropdown
# Feature: ui-konsistenz-verbesserungen, Property 2: Nur aktive Pflanzen im Ereignis-Dropdown
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    plant_entries=st.lists(_plant_entry, min_size=1, max_size=8).filter(
        lambda entries: len({e["name"] for e in entries}) == len(entries)
    ),
)
def test_nur_aktive_pflanzen_im_ereignis_dropdown(plant_entries):
    """For any mix of active and inactive plants, the /beobachtungen page
    event form dropdown contains ONLY active plants and NO inactive plants.

    # Feature: ui-konsistenz-verbesserungen, Property 2: Nur aktive Pflanzen im Ereignis-Dropdown

    **Validates: Requirements 3.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)

        active_names = set()
        inactive_names = set()

        # Use db_mod directly (same module object as app uses after reload)
        for entry in plant_entries:
            db_mod.add_plant(
                name=entry["name"], type="Gemüse", variety=None,
                lichtbedarf="Sonne", kommentar=None, kategorie="Gemüse",
                farbe=None,
            )
            if not entry["aktiv"]:
                all_plants = db_mod.get_all_plants(include_inactive=True)
                pid = next(p["id"] for p in all_plants if p["name"] == entry["name"])
                db_mod.set_plant_active(pid, 0)
            if entry["aktiv"]:
                active_names.add(entry["name"])
            else:
                inactive_names.add(entry["name"])

        with app_module.app.test_client() as client:
            resp = client.get("/beobachtungen")
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

        # Parse the plant_id <select> dropdown options from the HTML
        # Use a simple regex approach for robustness
        import re
        # Extract the <select name="plant_id"> ... </select> block
        select_match = re.search(
            r'<select\s+name="plant_id"[^>]*>(.*?)</select>',
            html, re.DOTALL,
        )
        assert select_match, "Could not find <select name='plant_id'> in HTML"
        select_html = select_match.group(1)

        # Extract all <option value="...">TEXT</option> entries
        option_matches = re.findall(
            r'<option\s+value="([^"]*)"[^>]*>(.*?)</option>',
            select_html, re.DOTALL,
        )
        # Filter out the placeholder option
        dropdown_names = set()
        for value, text in option_matches:
            text = text.strip()
            if value and text:
                dropdown_names.add(text)
        # All active plants must appear in the dropdown
        for name in active_names:
            assert name in dropdown_names, (
                f"Active plant '{name}' missing from dropdown. "
                f"Dropdown contains: {dropdown_names}"
            )

        # No inactive plant may appear in the dropdown
        for name in inactive_names:
            assert name not in dropdown_names, (
                f"Inactive plant '{name}' found in dropdown but should not be. "
                f"Dropdown contains: {dropdown_names}"
            )


# ---------------------------------------------------------------------------
# Property 3: Gültiges Ereignis wird über Tagebuchseite gespeichert
# Feature: ui-konsistenz-verbesserungen, Property 3: Gültiges Ereignis wird gespeichert
# ---------------------------------------------------------------------------

_ZEITRAUM_EREIGNISTYPEN = {"Blüte", "Ernte"}
_VALID_DETAIL = ["", "Anfang", "Mitte", "Ende"]


@st.composite
def _valid_ereignis_data(draw):
    """Generate valid event form data for POST /ereignis/add.

    For period events (Blüte, Ernte): startmonat <= endmonat.
    For non-period events: only startmonat matters (endmonat set by route).
    """
    ereignistyp = draw(st.sampled_from(_VALID_EREIGNISTYPEN))
    startmonat = draw(st.integers(min_value=1, max_value=12))
    start_detail = draw(st.sampled_from(_VALID_DETAIL))
    end_detail = draw(st.sampled_from(_VALID_DETAIL))

    if ereignistyp in _ZEITRAUM_EREIGNISTYPEN:
        endmonat = draw(st.integers(min_value=startmonat, max_value=12))
    else:
        endmonat = startmonat

    return {
        "ereignistyp": ereignistyp,
        "startmonat": startmonat,
        "endmonat": endmonat,
        "start_detail": start_detail,
        "end_detail": end_detail,
    }


@settings(max_examples=100, deadline=None)
@given(data=_valid_ereignis_data())
def test_gueltiges_ereignis_wird_ueber_tagebuchseite_gespeichert(data):
    """For any valid combination of active plant, valid event type, and valid
    months (1-12), POST /ereignis/add saves the event and redirects to
    /beobachtungen.

    # Feature: ui-konsistenz-verbesserungen, Property 3: Gültiges Ereignis wird gespeichert

    **Validates: Requirements 3.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)

        # Create an active plant
        plant_id = _add_plant(db_path, name="Testpflanze", aktiv=True)

        form_data = {
            "plant_id": str(plant_id),
            "ereignistyp": data["ereignistyp"],
            "startmonat": str(data["startmonat"]),
            "start_detail": data["start_detail"],
        }

        if data["ereignistyp"] in _ZEITRAUM_EREIGNISTYPEN:
            form_data["endmonat"] = str(data["endmonat"])
            form_data["end_detail"] = data["end_detail"]

        with app_module.app.test_client() as client:
            resp = client.post("/ereignis/add", data=form_data)

            # Should redirect (302) to /beobachtungen
            assert resp.status_code == 302, (
                f"Expected 302 redirect, got {resp.status_code}"
            )
            assert "/beobachtungen" in resp.headers.get("Location", ""), (
                f"Expected redirect to /beobachtungen, got {resp.headers.get('Location')}"
            )

        # Verify the event was saved in the DB
        plant = db_mod.get_plant(plant_id)
        assert plant is not None, "Plant should still exist"
        ereignisse = plant["ereignisse"]
        assert len(ereignisse) == 1, (
            f"Expected exactly 1 ereignis, got {len(ereignisse)}"
        )

        saved = ereignisse[0]
        assert saved["ereignistyp"] == data["ereignistyp"]
        assert saved["startmonat"] == data["startmonat"]

        if data["ereignistyp"] in _ZEITRAUM_EREIGNISTYPEN:
            assert saved["endmonat"] == data["endmonat"]
        else:
            # Non-period: endmonat should equal startmonat
            assert saved["endmonat"] == data["startmonat"]


# ---------------------------------------------------------------------------
# Property 4: Ungültiger Ereignistyp wird abgelehnt
# Feature: ui-konsistenz-verbesserungen, Property 4: Ungültiger Ereignistyp wird abgelehnt
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    invalid_ereignistyp=st.text().filter(lambda s: s not in set(_VALID_EREIGNISTYPEN)),
)
def test_ungueltiger_ereignistyp_wird_abgelehnt(invalid_ereignistyp):
    """For any string NOT in VALID_EREIGNISTYPEN, POST /ereignis/add must
    return 400 with error message and must NOT save any event.

    # Feature: ui-konsistenz-verbesserungen, Property 4: Ungültiger Ereignistyp wird abgelehnt

    **Validates: Requirements 3.7**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db_mod = _init_db(db_path)
        app_module = _get_test_client(db_path)

        # Create an active plant
        plant_id = _add_plant(db_path, name="Testpflanze", aktiv=True)

        form_data = {
            "plant_id": str(plant_id),
            "ereignistyp": invalid_ereignistyp,
            "startmonat": "6",
            "endmonat": "6",
            "start_detail": "",
            "end_detail": "",
        }

        with app_module.app.test_client() as client:
            resp = client.post("/ereignis/add", data=form_data)

            # Must return 400
            assert resp.status_code == 400, (
                f"Expected 400 for invalid ereignistyp {invalid_ereignistyp!r}, "
                f"got {resp.status_code}"
            )

            # Must contain the error message
            html = resp.data.decode("utf-8")
            assert "Ereignistyp ungültig." in html, (
                f"Expected error message 'Ereignistyp ungültig.' in response "
                f"for invalid ereignistyp {invalid_ereignistyp!r}"
            )

        # Verify no event was saved in the DB
        plant = db_mod.get_plant(plant_id)
        assert plant is not None, "Plant should still exist"
        assert len(plant["ereignisse"]) == 0, (
            f"Expected 0 ereignisse for invalid type {invalid_ereignistyp!r}, "
            f"got {len(plant['ereignisse'])}"
        )
