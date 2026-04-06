"""Property-based tests for the pflanze-inaktiv feature (Hypothesis).

# Feature: pflanze-inaktiv
"""
import importlib
import os
import tempfile

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


# ---------------------------------------------------------------------------
# Strategies for valid plant data
# ---------------------------------------------------------------------------

VALID_LICHTBEDARF = ["Sonne", "Halbschatten", "Schatten"]
VALID_KATEGORIEN = ["Obst", "Gemüse", "Kräuter", "Stauden", "Gehölze", "Blumen", "Gründüngung"]
VALID_LEBENSDAUER = ["Einjährig", "Zweijährig", "Mehrjährig"]

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

optional_text_st = st.one_of(st.none(), st.text(max_size=50))
lichtbedarf_st = st.sampled_from(VALID_LICHTBEDARF)
kategorie_st = st.one_of(st.none(), st.sampled_from(VALID_KATEGORIEN))
lebensdauer_st = st.one_of(st.none(), st.sampled_from(VALID_LEBENSDAUER))
pflanzmonat_st = st.one_of(st.none(), st.integers(min_value=1, max_value=12))
pflanzjahr_st = st.one_of(st.none(), st.integers(min_value=2000, max_value=2099))
anzahl_st = st.integers(min_value=1, max_value=999)


def _init_db(db_path: str):
    """Initialise an isolated SQLite database and return the reloaded db module."""
    os.environ["DB_PATH"] = db_path

    import db as db_module
    importlib.reload(db_module)
    db_module.init_db()
    return db_module


# ---------------------------------------------------------------------------
# Property 1: Neue Pflanzen sind standardmäßig aktiv
# Feature: pflanze-inaktiv, Property 1: Neue Pflanzen sind standardmäßig aktiv
# ---------------------------------------------------------------------------

@settings(max_examples=20)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    variety=optional_text_st,
    lichtbedarf=lichtbedarf_st,
    kommentar=optional_text_st,
    lebensdauer=lebensdauer_st,
    pflanzmonat=pflanzmonat_st,
    pflanzjahr=pflanzjahr_st,
    anzahl=anzahl_st,
    kategorie=kategorie_st,
    beschreibung=optional_text_st,
    farbe=optional_text_st,
)
def test_new_plants_are_active(
    name,
    type_,
    variety,
    lichtbedarf,
    kommentar,
    lebensdauer,
    pflanzmonat,
    pflanzjahr,
    anzahl,
    kategorie,
    beschreibung,
    farbe,
):
    """For any plant with random valid data, after adding via add_plant(),
    the plant has aktiv = 1.

    # Feature: pflanze-inaktiv, Property 1: Neue Pflanzen sind standardmäßig aktiv

    **Validates: Requirements 1.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        db.add_plant(
            name=name,
            type=type_,
            variety=variety,
            lichtbedarf=lichtbedarf,
            kommentar=kommentar,
            lebensdauer=lebensdauer,
            pflanzmonat=pflanzmonat,
            pflanzjahr=pflanzjahr,
            anzahl=anzahl,
            kategorie=kategorie,
            beschreibung=beschreibung,
            farbe=farbe,
        )

        # Retrieve all plants (including inactive) to verify
        plants = db.get_all_plants(include_inactive=True)
        assert len(plants) >= 1

        # The most recently added plant should be the last one
        added_plant = plants[-1]
        assert added_plant["aktiv"] == 1, (
            f"Expected aktiv=1 for newly added plant '{name}', "
            f"got aktiv={added_plant['aktiv']}"
        )


# ---------------------------------------------------------------------------
# Property 2: Deaktivieren-Aktivieren Round-Trip
# Feature: pflanze-inaktiv, Property 2: Deaktivieren-Aktivieren Round-Trip
# ---------------------------------------------------------------------------

@settings(max_examples=20)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    variety=optional_text_st,
    lichtbedarf=lichtbedarf_st,
    kommentar=optional_text_st,
    lebensdauer=lebensdauer_st,
    pflanzmonat=pflanzmonat_st,
    pflanzjahr=pflanzjahr_st,
    anzahl=anzahl_st,
    kategorie=kategorie_st,
    beschreibung=optional_text_st,
    farbe=optional_text_st,
)
def test_deactivate_activate_roundtrip(
    name,
    type_,
    variety,
    lichtbedarf,
    kommentar,
    lebensdauer,
    pflanzmonat,
    pflanzjahr,
    anzahl,
    kategorie,
    beschreibung,
    farbe,
):
    """For any active plant, deactivate sets aktiv=0, then activate sets aktiv=1 (round-trip).

    # Feature: pflanze-inaktiv, Property 2: Deaktivieren-Aktivieren Round-Trip

    **Validates: Requirements 2.2, 3.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a new plant (starts as aktiv=1)
        db.add_plant(
            name=name,
            type=type_,
            variety=variety,
            lichtbedarf=lichtbedarf,
            kommentar=kommentar,
            lebensdauer=lebensdauer,
            pflanzmonat=pflanzmonat,
            pflanzjahr=pflanzjahr,
            anzahl=anzahl,
            kategorie=kategorie,
            beschreibung=beschreibung,
            farbe=farbe,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Deactivate: aktiv should become 0
        db.set_plant_active(plant_id, 0)
        plant_after_deactivate = db.get_plant(plant_id)
        assert plant_after_deactivate["aktiv"] == 0, (
            f"Expected aktiv=0 after deactivation for plant '{name}', "
            f"got aktiv={plant_after_deactivate['aktiv']}"
        )

        # Activate: aktiv should become 1 again (round-trip)
        db.set_plant_active(plant_id, 1)
        plant_after_activate = db.get_plant(plant_id)
        assert plant_after_activate["aktiv"] == 1, (
            f"Expected aktiv=1 after re-activation for plant '{name}', "
            f"got aktiv={plant_after_activate['aktiv']}"
        )


# ---------------------------------------------------------------------------
# Strategies for events and observations
# ---------------------------------------------------------------------------

VALID_EREIGNISTYPEN = ["Blüte", "Ernte", "Düngen", "Rückschnitt", "Vorkultur", "Auspflanzen", "Direktsaat"]
VALID_DETAILS = [None, "Anfang", "Mitte", "Ende"]

ereignistyp_st = st.sampled_from(VALID_EREIGNISTYPEN)
monat_st = st.integers(min_value=1, max_value=12)
detail_st = st.sampled_from(VALID_DETAILS)

# Strategy for a list of events (0–5 per plant)
ereignis_st = st.lists(
    st.tuples(ereignistyp_st, monat_st, monat_st, detail_st, detail_st),
    min_size=0,
    max_size=5,
)

# Strategy for a list of observations (0–5 per plant)
beobachtung_st = st.lists(
    st.tuples(
        st.integers(min_value=2020, max_value=2025),  # jahr
        ereignistyp_st,
        monat_st,  # startmonat
        monat_st,  # endmonat
        st.one_of(st.none(), st.text(max_size=20)),  # phaenologische_phase
        st.one_of(st.none(), st.text(max_size=50)),  # notiz
        detail_st,  # start_detail
        detail_st,  # end_detail
    ),
    min_size=0,
    max_size=5,
)


# ---------------------------------------------------------------------------
# Property 3: Deaktivierung bewahrt alle Daten (Invariante)
# Feature: pflanze-inaktiv, Property 3: Deaktivierung bewahrt alle Daten
# ---------------------------------------------------------------------------

@settings(max_examples=20)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    variety=optional_text_st,
    lichtbedarf=lichtbedarf_st,
    kommentar=optional_text_st,
    lebensdauer=lebensdauer_st,
    pflanzmonat=pflanzmonat_st,
    pflanzjahr=pflanzjahr_st,
    anzahl=anzahl_st,
    kategorie=kategorie_st,
    beschreibung=optional_text_st,
    farbe=optional_text_st,
    ereignisse=ereignis_st,
    beobachtungen=beobachtung_st,
)
def test_deactivation_preserves_data(
    name,
    type_,
    variety,
    lichtbedarf,
    kommentar,
    lebensdauer,
    pflanzmonat,
    pflanzjahr,
    anzahl,
    kategorie,
    beschreibung,
    farbe,
    ereignisse,
    beobachtungen,
):
    """For any plant with random data (including events/observations), after
    deactivation ALL data except `aktiv` remains unchanged.

    # Feature: pflanze-inaktiv, Property 3: Deaktivierung bewahrt alle Daten

    **Validates: Requirements 2.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a plant
        db.add_plant(
            name=name,
            type=type_,
            variety=variety,
            lichtbedarf=lichtbedarf,
            kommentar=kommentar,
            lebensdauer=lebensdauer,
            pflanzmonat=pflanzmonat,
            pflanzjahr=pflanzjahr,
            anzahl=anzahl,
            kategorie=kategorie,
            beschreibung=beschreibung,
            farbe=farbe,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Add events
        for ereignistyp, startmonat, endmonat, start_detail, end_detail in ereignisse:
            sm, em = min(startmonat, endmonat), max(startmonat, endmonat)
            db.add_ereignis(plant_id, ereignistyp, sm, em, start_detail, end_detail)

        # Add observations
        for jahr, ereignistyp, startmonat, endmonat, phase, notiz, start_detail, end_detail in beobachtungen:
            sm, em = min(startmonat, endmonat), max(startmonat, endmonat)
            db.add_beobachtung(plant_id, jahr, ereignistyp, sm, em, phase, notiz, start_detail, end_detail)

        # Snapshot BEFORE deactivation
        plant_before = db.get_plant(plant_id)
        assert plant_before is not None
        assert plant_before["aktiv"] == 1

        # Deactivate
        db.set_plant_active(plant_id, 0)

        # Snapshot AFTER deactivation
        plant_after = db.get_plant(plant_id)
        assert plant_after is not None
        assert plant_after["aktiv"] == 0

        # All plant fields except 'aktiv' must be identical
        PLANT_FIELDS = [
            "name", "type", "variety", "lichtbedarf", "kommentar",
            "lebensdauer", "pflanzmonat", "pflanzjahr", "anzahl",
            "kategorie", "beschreibung", "farbe",
        ]
        for field in PLANT_FIELDS:
            assert plant_before[field] == plant_after[field], (
                f"Field '{field}' changed after deactivation: "
                f"{plant_before[field]!r} → {plant_after[field]!r}"
            )

        # Events must be identical
        assert plant_before["ereignisse"] == plant_after["ereignisse"], (
            "Ereignisse changed after deactivation"
        )

        # Observations must be identical
        assert plant_before["beobachtungen"] == plant_after["beobachtungen"], (
            "Beobachtungen changed after deactivation"
        )


# ---------------------------------------------------------------------------
# Property 4: Kontextabhängiger Button auf der Bearbeitungsseite
# Feature: pflanze-inaktiv, Property 4: Kontextabhängiger Button auf der Bearbeitungsseite
# ---------------------------------------------------------------------------

@settings(max_examples=20, deadline=None)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    lichtbedarf=lichtbedarf_st,
    kategorie=st.sampled_from(VALID_KATEGORIEN),
    aktiv_status=st.sampled_from([0, 1]),
)
def test_context_dependent_button(
    name,
    type_,
    lichtbedarf,
    kategorie,
    aktiv_status,
):
    """For any plant, the edit page shows exactly one of two buttons:
    'Inaktiv setzen' when aktiv=1, or 'Aktivieren' when aktiv=0.
    The other button must NOT be present.

    # Feature: pflanze-inaktiv, Property 4: Kontextabhängiger Button auf der Bearbeitungsseite

    **Validates: Requirements 2.1, 3.1, 5.2**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a plant
        db.add_plant(
            name=name,
            type=type_,
            variety=None,
            lichtbedarf=lichtbedarf,
            kommentar=None,
            kategorie=kategorie,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Set the desired active status
        db.set_plant_active(plant_id, aktiv_status)

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            response = client.get(f"/plant/{plant_id}/edit")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            if aktiv_status == 1:
                # Active plant: must show "Inaktiv setzen", must NOT show "Aktivieren" button
                assert "Inaktiv setzen" in html, (
                    f"Expected 'Inaktiv setzen' button for active plant '{name}'"
                )
                # The "Aktivieren" button is inside a form posting to /activate
                assert f"/plant/{plant_id}/activate" not in html, (
                    f"'Aktivieren' button should NOT be present for active plant '{name}'"
                )
            else:
                # Inactive plant: must show "Aktivieren", must NOT show "Inaktiv setzen" button
                assert "Aktivieren" in html, (
                    f"Expected 'Aktivieren' button for inactive plant '{name}'"
                )
                # The "Inaktiv setzen" button is inside a form posting to /deactivate
                assert f"/plant/{plant_id}/deactivate" not in html, (
                    f"'Inaktiv setzen' button should NOT be present for inactive plant '{name}'"
                )


# ---------------------------------------------------------------------------
# Property 5: Korrektes Redirect-Verhalten nach Statusänderung
# Feature: pflanze-inaktiv, Property 5: Korrektes Redirect-Verhalten nach Statusänderung
# ---------------------------------------------------------------------------

@settings(max_examples=20, deadline=None)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    lichtbedarf=lichtbedarf_st,
    kategorie=st.sampled_from(VALID_KATEGORIEN),
)
def test_redirect_after_status_change(
    name,
    type_,
    lichtbedarf,
    kategorie,
):
    """For any existing plant, POST /plant/<id>/deactivate returns HTTP 302
    redirect to /, and POST /plant/<id>/activate returns HTTP 302 redirect
    to /plant/<id>/edit.

    # Feature: pflanze-inaktiv, Property 5: Korrektes Redirect-Verhalten nach Statusänderung

    **Validates: Requirements 2.4, 3.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a plant (starts as aktiv=1)
        db.add_plant(
            name=name,
            type=type_,
            variety=None,
            lichtbedarf=lichtbedarf,
            kommentar=None,
            kategorie=kategorie,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            # --- Deactivate: POST should return 302 redirect to / ---
            resp_deactivate = client.post(
                f"/plant/{plant_id}/deactivate",
                follow_redirects=False,
            )
            assert resp_deactivate.status_code == 302, (
                f"Expected 302 for deactivate, got {resp_deactivate.status_code}"
            )
            deactivate_location = resp_deactivate.headers.get("Location", "")
            assert deactivate_location.endswith("/"), (
                f"Expected deactivate redirect to '/', got '{deactivate_location}'"
            )

            # --- Activate: POST should return 302 redirect to /plant/<id>/edit ---
            resp_activate = client.post(
                f"/plant/{plant_id}/activate",
                follow_redirects=False,
            )
            assert resp_activate.status_code == 302, (
                f"Expected 302 for activate, got {resp_activate.status_code}"
            )
            activate_location = resp_activate.headers.get("Location", "")
            assert activate_location.endswith(f"/plant/{plant_id}/edit"), (
                f"Expected activate redirect to '/plant/{plant_id}/edit', "
                f"got '{activate_location}'"
            )


# ---------------------------------------------------------------------------
# Property 6: Filterverhalten der Pflanzenliste
# Feature: pflanze-inaktiv, Property 6: Filterverhalten der Pflanzenliste
# ---------------------------------------------------------------------------

_unique_name_st = st.text(
    alphabet=st.characters(whitelist_categories=("L",)),
    min_size=8,
    max_size=20,
).map(lambda s: f"TESTPFLANZE_{s}")


@settings(max_examples=20, deadline=None)
@given(
    plants_data=st.lists(
        st.tuples(
            _unique_name_st,
            plant_type_st,
            lichtbedarf_st,
            st.sampled_from(VALID_KATEGORIEN),
            st.booleans(),  # should_deactivate
        ),
        min_size=2,
        max_size=5,
    ),
)
def test_filter_active_inactive(plants_data):
    """For any mix of active and inactive plants, GET `/` shows only active
    plants, GET `/?show_inactive=1` shows all plants.

    # Feature: pflanze-inaktiv, Property 6: Filterverhalten der Pflanzenliste

    **Validates: Requirements 4.1, 4.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        active_names = []
        all_names = []

        for name, type_, lichtbedarf, kategorie, should_deactivate in plants_data:
            db.add_plant(
                name=name,
                type=type_,
                variety=None,
                lichtbedarf=lichtbedarf,
                kommentar=None,
                kategorie=kategorie,
            )
            plants = db.get_all_plants(include_inactive=True)
            plant_id = plants[-1]["id"]

            all_names.append(name)
            if should_deactivate:
                db.set_plant_active(plant_id, 0)
            else:
                active_names.append(name)

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            # --- GET / (default): should show only active plants ---
            resp_default = client.get("/")
            assert resp_default.status_code == 200
            html_default = resp_default.data.decode("utf-8")

            for name in active_names:
                assert name in html_default, (
                    f"Active plant '{name}' should appear on default index page"
                )

            inactive_names = [n for n in all_names if n not in active_names]
            for name in inactive_names:
                assert name not in html_default, (
                    f"Inactive plant '{name}' should NOT appear on default index page"
                )

            # --- GET /?show_inactive=1: should show ALL plants ---
            resp_all = client.get("/?show_inactive=1")
            assert resp_all.status_code == 200
            html_all = resp_all.data.decode("utf-8")

            for name in all_names:
                assert name in html_all, (
                    f"Plant '{name}' should appear on index page with show_inactive=1"
                )


# ---------------------------------------------------------------------------
# Property 7: Visuelle Kennzeichnung inaktiver Pflanzen
# Feature: pflanze-inaktiv, Property 7: Visuelle Kennzeichnung inaktiver Pflanzen
# ---------------------------------------------------------------------------

@settings(max_examples=20, deadline=None)
@given(
    name=_unique_name_st,
    type_=plant_type_st,
    lichtbedarf=lichtbedarf_st,
    kategorie=st.sampled_from(VALID_KATEGORIEN),
)
def test_visual_marking_inactive(
    name,
    type_,
    lichtbedarf,
    kategorie,
):
    """For any inactive plant shown in the list (via show_inactive=1), its table
    row has the CSS class 'row-inactive' and a badge 'inaktiv'. On the edit page,
    the hint 'Diese Pflanze ist inaktiv' is present.

    # Feature: pflanze-inaktiv, Property 7: Visuelle Kennzeichnung inaktiver Pflanzen

    **Validates: Requirements 4.4, 5.1**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a plant and deactivate it
        db.add_plant(
            name=name,
            type=type_,
            variety=None,
            lichtbedarf=lichtbedarf,
            kommentar=None,
            kategorie=kategorie,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]
        db.set_plant_active(plant_id, 0)

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            # --- List page with show_inactive=1 ---
            resp_list = client.get("/?show_inactive=1")
            assert resp_list.status_code == 200
            html_list = resp_list.data.decode("utf-8")

            assert "row-inactive" in html_list, (
                f"Expected 'row-inactive' CSS class for inactive plant '{name}' in list"
            )
            assert "badge-inactive" in html_list, (
                f"Expected 'badge-inactive' badge for inactive plant '{name}' in list"
            )
            # The badge text "inaktiv" should appear
            assert ">inaktiv<" in html_list, (
                f"Expected badge text 'inaktiv' for inactive plant '{name}' in list"
            )

            # --- Edit page ---
            resp_edit = client.get(f"/plant/{plant_id}/edit")
            assert resp_edit.status_code == 200
            html_edit = resp_edit.data.decode("utf-8")

            assert "Diese Pflanze ist inaktiv" in html_edit, (
                f"Expected 'Diese Pflanze ist inaktiv' hint on edit page for '{name}'"
            )


# ---------------------------------------------------------------------------
# Property 8: Bearbeitungsseite funktioniert für inaktive Pflanzen
# Feature: pflanze-inaktiv, Property 8: Bearbeitungsseite funktioniert für inaktive Pflanzen
# ---------------------------------------------------------------------------

@settings(max_examples=20, deadline=None)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    lichtbedarf=lichtbedarf_st,
    kategorie=st.sampled_from(VALID_KATEGORIEN),
    ereignisse=ereignis_st,
    beobachtungen=beobachtung_st,
)
def test_edit_page_works_for_inactive(
    name,
    type_,
    lichtbedarf,
    kategorie,
    ereignisse,
    beobachtungen,
):
    """For any inactive plant with events and observations, the edit page shows
    all form fields, all events, all observations, the event add form, the
    observation add form, and the delete button.

    # Feature: pflanze-inaktiv, Property 8: Bearbeitungsseite funktioniert für inaktive Pflanzen

    **Validates: Requirements 6.1, 6.2, 6.3**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a plant
        db.add_plant(
            name=name,
            type=type_,
            variety=None,
            lichtbedarf=lichtbedarf,
            kommentar=None,
            kategorie=kategorie,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Add events
        for ereignistyp, startmonat, endmonat, start_detail, end_detail in ereignisse:
            sm, em = min(startmonat, endmonat), max(startmonat, endmonat)
            db.add_ereignis(plant_id, ereignistyp, sm, em, start_detail, end_detail)

        # Add observations
        for jahr, ereignistyp, startmonat, endmonat, phase, notiz, start_detail, end_detail in beobachtungen:
            sm, em = min(startmonat, endmonat), max(startmonat, endmonat)
            db.add_beobachtung(plant_id, jahr, ereignistyp, sm, em, phase, notiz, start_detail, end_detail)

        # Deactivate the plant
        db.set_plant_active(plant_id, 0)

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            resp = client.get(f"/plant/{plant_id}/edit")
            assert resp.status_code == 200
            html = resp.data.decode("utf-8")

            # Form fields present (Stammdaten)
            assert 'name="name"' in html, "Expected 'name' form field on edit page"
            assert 'name="kategorie"' in html, "Expected 'kategorie' form field"
            assert 'name="lichtbedarf"' in html, "Expected 'lichtbedarf' form field"
            assert 'name="kommentar"' in html, "Expected 'kommentar' form field"

            # Event add form present
            assert f"/plant/{plant_id}/ereignis/add" in html, (
                "Expected event add form on edit page for inactive plant"
            )

            # Observation add form present
            assert f"/plant/{plant_id}/beobachtung/add" in html, (
                "Expected observation add form on edit page for inactive plant"
            )

            # Delete button present
            assert f"/remove/{plant_id}" in html, (
                "Expected delete button on edit page for inactive plant"
            )

            # Verify events are shown
            plant_data = db.get_plant(plant_id)
            for e in plant_data["ereignisse"]:
                assert e["ereignistyp"] in html, (
                    f"Expected event '{e['ereignistyp']}' on edit page for inactive plant"
                )

            # Verify observations are shown
            for b in plant_data["beobachtungen"]:
                assert str(b["jahr"]) in html, (
                    f"Expected observation year '{b['jahr']}' on edit page for inactive plant"
                )


# ---------------------------------------------------------------------------
# Property 9: Duplikat einer inaktiven Pflanze ist aktiv
# Feature: pflanze-inaktiv, Property 9: Duplikat einer inaktiven Pflanze ist aktiv
# ---------------------------------------------------------------------------

@settings(max_examples=20)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    variety=optional_text_st,
    lichtbedarf=lichtbedarf_st,
    kommentar=optional_text_st,
    lebensdauer=lebensdauer_st,
    pflanzmonat=pflanzmonat_st,
    pflanzjahr=pflanzjahr_st,
    anzahl=anzahl_st,
    kategorie=kategorie_st,
    beschreibung=optional_text_st,
    farbe=optional_text_st,
)
def test_duplicate_inactive_is_active(
    name,
    type_,
    variety,
    lichtbedarf,
    kommentar,
    lebensdauer,
    pflanzmonat,
    pflanzjahr,
    anzahl,
    kategorie,
    beschreibung,
    farbe,
):
    """For any inactive plant, after duplicating via duplicate_plant(),
    the duplicate has aktiv = 1.

    # Feature: pflanze-inaktiv, Property 9: Duplikat einer inaktiven Pflanze ist aktiv

    **Validates: Requirements 7.1**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add a plant
        db.add_plant(
            name=name,
            type=type_,
            variety=variety,
            lichtbedarf=lichtbedarf,
            kommentar=kommentar,
            lebensdauer=lebensdauer,
            pflanzmonat=pflanzmonat,
            pflanzjahr=pflanzjahr,
            anzahl=anzahl,
            kategorie=kategorie,
            beschreibung=beschreibung,
            farbe=farbe,
        )

        plants = db.get_all_plants(include_inactive=True)
        plant_id = plants[-1]["id"]

        # Deactivate the source plant
        db.set_plant_active(plant_id, 0)
        source = db.get_plant(plant_id)
        assert source["aktiv"] == 0, "Source plant should be inactive before duplication"

        # Duplicate
        new_id = db.duplicate_plant(plant_id)

        # Verify duplicate is active
        duplicate = db.get_plant(new_id)
        assert duplicate is not None, "Duplicate plant should exist"
        assert duplicate["aktiv"] == 1, (
            f"Expected aktiv=1 for duplicate of inactive plant '{name}', "
            f"got aktiv={duplicate['aktiv']}"
        )
