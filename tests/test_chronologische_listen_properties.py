"""Property-based tests for the chronologische-listen feature (Hypothesis).

# Feature: chronologische-listen
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from db import berechne_sortierwert


# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

VALID_DETAILS = ["Anfang", "Mitte", "Ende"]
DETAIL_OFFSETS = {"Anfang": 5, "Mitte": 15, "Ende": 25}

monat_st = st.integers(min_value=1, max_value=12)
detail_st = st.sampled_from(VALID_DETAILS + [None])


# ---------------------------------------------------------------------------
# Property 1: Sortierwert-Berechnung
# Feature: chronologische-listen, Property 1: Sortierwert-Berechnung
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(monat=monat_st, detail=detail_st)
def test_sortierwert_berechnung(monat, detail):
    """For any month (1-12) and detail ('Anfang', 'Mitte', 'Ende', None),
    berechne_sortierwert returns monat * 100 + offset where offset is
    5 for 'Anfang', 15 for 'Mitte' or None, 25 for 'Ende'.

    # Feature: chronologische-listen, Property 1: Sortierwert-Berechnung

    **Validates: Requirements 4.1, 4.2, 4.3, 4.4**
    """
    result = berechne_sortierwert(monat, detail)

    if detail == "Anfang":
        expected_offset = 5
    elif detail == "Ende":
        expected_offset = 25
    else:  # "Mitte" or None
        expected_offset = 15

    expected = monat * 100 + expected_offset
    assert result == expected, (
        f"berechne_sortierwert({monat}, {detail!r}) = {result}, expected {expected}"
    )


# ---------------------------------------------------------------------------
# Helpers & Strategies for DB-level tests
# ---------------------------------------------------------------------------

import importlib
import os
import tempfile

VALID_LICHTBEDARF = ["Sonne", "Halbschatten", "Schatten"]
VALID_KATEGORIEN = ["Obst", "Gemüse", "Kräuter", "Stauden", "Sträucher", "Bäume", "Blumen", "Gründüngung"]
VALID_LEBENSDAUER = ["Einjährig", "Zweijährig", "Mehrjährig"]
VALID_EREIGNISTYPEN = ["Blüte", "Ernte", "Düngen", "Rückschnitt", "Vorkultur", "Auspflanzen", "Direktsaat"]

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
kategorie_st = st.one_of(st.none(), st.sampled_from(VALID_KATEGORIEN))
ereignistyp_st = st.sampled_from(VALID_EREIGNISTYPEN)
db_monat_st = st.integers(min_value=1, max_value=12)
db_detail_st = st.sampled_from([None, "Anfang", "Mitte", "Ende"])

# Strategy: a single plant record (name, type, lichtbedarf, kategorie, should_deactivate)
plant_record_st = st.tuples(
    plant_name_st, plant_type_st, lichtbedarf_st, kategorie_st, st.booleans()
)

# Strategy: list of events per plant (0–3)
ereignis_list_st = st.lists(
    st.tuples(ereignistyp_st, db_monat_st, db_monat_st, db_detail_st, db_detail_st),
    min_size=0,
    max_size=3,
)

# Strategy: list of observations per plant (0–3)
beobachtung_list_st = st.lists(
    st.tuples(
        st.integers(min_value=2020, max_value=2025),  # jahr
        ereignistyp_st,
        db_monat_st,  # startmonat
        db_monat_st,  # endmonat
        db_detail_st,  # start_detail
        db_detail_st,  # end_detail
    ),
    min_size=0,
    max_size=3,
)


def _init_db(db_path: str):
    """Initialise an isolated SQLite database and return the reloaded db module."""
    os.environ["DB_PATH"] = db_path
    import db as db_module
    importlib.reload(db_module)
    db_module.init_db()
    return db_module


# ---------------------------------------------------------------------------
# Property 2: Nur aktive Pflanzen in beiden Listen
# Feature: chronologische-listen, Property 2: Nur aktive Pflanzen in beiden Listen
# ---------------------------------------------------------------------------

@settings(max_examples=100)
@given(
    plants=st.lists(plant_record_st, min_size=1, max_size=6),
    ereignisse_per_plant=st.lists(ereignis_list_st, min_size=6, max_size=6),
    beobachtungen_per_plant=st.lists(beobachtung_list_st, min_size=6, max_size=6),
)
def test_nur_aktive_pflanzen(plants, ereignisse_per_plant, beobachtungen_per_plant):
    """For any random mix of active/inactive plants with observations and events,
    get_all_beobachtungen() and get_all_ereignisse() return only entries from
    plants with aktiv = 1.

    # Feature: chronologische-listen, Property 2: Nur aktive Pflanzen in beiden Listen

    **Validates: Requirements 2.1, 3.1**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        active_plant_ids = set()
        inactive_plant_ids = set()

        for i, (name, type_, lichtbedarf, kategorie, should_deactivate) in enumerate(plants):
            db.add_plant(
                name=name,
                type=type_,
                variety=None,
                lichtbedarf=lichtbedarf,
                kommentar=None,
                kategorie=kategorie,
            )
            all_plants = db.get_all_plants(include_inactive=True)
            plant_id = all_plants[-1]["id"]

            # Add events for this plant
            for ereignistyp, sm, em, sd, ed in ereignisse_per_plant[i % len(ereignisse_per_plant)]:
                s, e = min(sm, em), max(sm, em)
                db.add_ereignis(plant_id, ereignistyp, s, e, sd, ed)

            # Add observations for this plant
            for jahr, ereignistyp, sm, em, sd, ed in beobachtungen_per_plant[i % len(beobachtungen_per_plant)]:
                s, e = min(sm, em), max(sm, em)
                db.add_beobachtung(plant_id, jahr, ereignistyp, s, e, None, None, sd, ed)

            # Deactivate some plants
            if should_deactivate:
                db.set_plant_active(plant_id, 0)
                inactive_plant_ids.add(plant_id)
            else:
                active_plant_ids.add(plant_id)

        # --- Assert: get_all_beobachtungen returns only active plants ---
        beobachtungen = db.get_all_beobachtungen()
        for b in beobachtungen:
            assert b["plant_id"] in active_plant_ids, (
                f"Beobachtung for plant_id={b['plant_id']} returned, "
                f"but that plant is inactive. Active IDs: {active_plant_ids}"
            )
            assert b["plant_id"] not in inactive_plant_ids, (
                f"Beobachtung for inactive plant_id={b['plant_id']} should not appear"
            )

        # --- Assert: get_all_ereignisse returns only active plants ---
        ereignisse = db.get_all_ereignisse()
        for e in ereignisse:
            assert e["plant_id"] in active_plant_ids, (
                f"Ereignis for plant_id={e['plant_id']} returned, "
                f"but that plant is inactive. Active IDs: {active_plant_ids}"
            )
            assert e["plant_id"] not in inactive_plant_ids, (
                f"Ereignis for inactive plant_id={e['plant_id']} should not appear"
            )


# ---------------------------------------------------------------------------
# Property 3: Sortierung nach Sortierwert und Pflanzenname
# Feature: chronologische-listen, Property 3: Sortierung nach Sortierwert und Pflanzenname
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    plants=st.lists(plant_record_st, min_size=1, max_size=6),
    ereignisse_per_plant=st.lists(ereignis_list_st, min_size=6, max_size=6),
    beobachtungen_per_plant=st.lists(beobachtung_list_st, min_size=6, max_size=6),
)
def test_sortierung_nach_sortierwert_und_name(plants, ereignisse_per_plant, beobachtungen_per_plant):
    """For any set of observations/events returned by get_all_beobachtungen()
    and get_all_ereignisse(), the list is sorted ascending by sortierwert,
    and for equal sortierwert alphabetically by plant_name.

    # Feature: chronologische-listen, Property 3: Sortierung nach Sortierwert und Pflanzenname

    **Validates: Requirements 2.3, 2.4, 3.3, 3.4**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        for i, (name, type_, lichtbedarf, kategorie, should_deactivate) in enumerate(plants):
            db.add_plant(
                name=name,
                type=type_,
                variety=None,
                lichtbedarf=lichtbedarf,
                kommentar=None,
                kategorie=kategorie,
            )
            all_plants = db.get_all_plants(include_inactive=True)
            plant_id = all_plants[-1]["id"]

            for ereignistyp, sm, em, sd, ed in ereignisse_per_plant[i % len(ereignisse_per_plant)]:
                s, e = min(sm, em), max(sm, em)
                db.add_ereignis(plant_id, ereignistyp, s, e, sd, ed)

            for jahr, ereignistyp, sm, em, sd, ed in beobachtungen_per_plant[i % len(beobachtungen_per_plant)]:
                s, e = min(sm, em), max(sm, em)
                db.add_beobachtung(plant_id, jahr, ereignistyp, s, e, None, None, sd, ed)

            if should_deactivate:
                db.set_plant_active(plant_id, 0)

        # --- Assert: get_all_beobachtungen is sorted correctly ---
        beobachtungen = db.get_all_beobachtungen()
        for i in range(len(beobachtungen) - 1):
            curr = beobachtungen[i]
            nxt = beobachtungen[i + 1]
            assert curr["sortierwert"] <= nxt["sortierwert"], (
                f"Beobachtungen not sorted by sortierwert: "
                f"{curr['sortierwert']} > {nxt['sortierwert']} "
                f"(plants: {curr['plant_name']!r}, {nxt['plant_name']!r})"
            )
            if curr["sortierwert"] == nxt["sortierwert"]:
                assert curr["plant_name"] <= nxt["plant_name"], (
                    f"Beobachtungen with equal sortierwert not sorted by name: "
                    f"{curr['plant_name']!r} > {nxt['plant_name']!r} "
                    f"(sortierwert={curr['sortierwert']})"
                )

        # --- Assert: get_all_ereignisse is sorted correctly ---
        ereignisse = db.get_all_ereignisse()
        for i in range(len(ereignisse) - 1):
            curr = ereignisse[i]
            nxt = ereignisse[i + 1]
            assert curr["sortierwert"] <= nxt["sortierwert"], (
                f"Ereignisse not sorted by sortierwert: "
                f"{curr['sortierwert']} > {nxt['sortierwert']} "
                f"(plants: {curr['plant_name']!r}, {nxt['plant_name']!r})"
            )
            if curr["sortierwert"] == nxt["sortierwert"]:
                assert curr["plant_name"] <= nxt["plant_name"], (
                    f"Ereignisse with equal sortierwert not sorted by name: "
                    f"{curr['plant_name']!r} > {nxt['plant_name']!r} "
                    f"(sortierwert={curr['sortierwert']})"
                )


# ---------------------------------------------------------------------------
# German months mapping (mirrors app.py GERMAN_MONTHS)
# ---------------------------------------------------------------------------

GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

# Strategy for a non-empty note (printable text without HTML-breaking chars)
note_st = st.one_of(
    st.none(),
    st.text(
        alphabet=st.characters(whitelist_categories=("L", "N", "Zs")),
        min_size=1,
        max_size=40,
    ).filter(lambda s: s.strip() != ""),
)


# ---------------------------------------------------------------------------
# Property 4: Beobachtungen enthalten alle Pflichtfelder und Pflanzen-Link
# Feature: chronologische-listen, Property 4: Beobachtungen enthalten alle Pflichtfelder und Pflanzen-Link
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    lichtbedarf=lichtbedarf_st,
    kategorie=st.sampled_from(VALID_KATEGORIEN),
    jahr=st.integers(min_value=2020, max_value=2025),
    ereignistyp=ereignistyp_st,
    startmonat=db_monat_st,
    endmonat=db_monat_st,
    start_detail=db_detail_st,
    end_detail=db_detail_st,
    notiz=note_st,
)
def test_beobachtungen_pflichtfelder(
    name,
    type_,
    lichtbedarf,
    kategorie,
    jahr,
    ereignistyp,
    startmonat,
    endmonat,
    start_detail,
    end_detail,
    notiz,
):
    """For any observation of an active plant, the rendered Beobachtungsliste HTML
    contains the plant name as a link to /plant/<id>/edit, the year, the event type,
    the time range, and the note (if present).

    # Feature: chronologische-listen, Property 4: Beobachtungen enthalten alle Pflichtfelder und Pflanzen-Link

    **Validates: Requirements 2.2, 8.1**
    """
    sm, em = min(startmonat, endmonat), max(startmonat, endmonat)

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add an active plant
        db.add_plant(
            name=name,
            type=type_,
            variety=None,
            lichtbedarf=lichtbedarf,
            kommentar=None,
            kategorie=kategorie,
        )
        all_plants = db.get_all_plants(include_inactive=True)
        plant_id = all_plants[-1]["id"]

        # Add an observation
        db.add_beobachtung(
            plant_id, jahr, ereignistyp, sm, em,
            None, notiz, start_detail, end_detail,
        )

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            response = client.get("/beobachtungen")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            # Plant name as link to edit page
            expected_link = f'<a href="/plant/{plant_id}/edit">{name}</a>'
            assert expected_link in html, (
                f"Expected link '{expected_link}' in HTML"
            )

            # Year
            assert str(jahr) in html, (
                f"Expected year '{jahr}' in HTML"
            )

            # Event type
            assert ereignistyp in html, (
                f"Expected event type '{ereignistyp}' in HTML"
            )

            # Start month name (from german_months)
            start_month_name = GERMAN_MONTHS[sm]
            assert start_month_name in html, (
                f"Expected start month name '{start_month_name}' in HTML"
            )

            # Note (if present)
            if notiz:
                assert notiz in html, (
                    f"Expected note '{notiz}' in HTML"
                )


# ---------------------------------------------------------------------------
# Property 5: Ereignisse enthalten alle Pflichtfelder und Pflanzen-Link
# Feature: chronologische-listen, Property 5: Ereignisse enthalten alle Pflichtfelder und Pflanzen-Link
# ---------------------------------------------------------------------------

@settings(max_examples=100, deadline=None)
@given(
    name=plant_name_st,
    type_=plant_type_st,
    lichtbedarf=lichtbedarf_st,
    kategorie=st.sampled_from(VALID_KATEGORIEN),
    ereignistyp=ereignistyp_st,
    startmonat=db_monat_st,
    endmonat=db_monat_st,
    start_detail=db_detail_st,
    end_detail=db_detail_st,
)
def test_ereignisse_pflichtfelder(
    name,
    type_,
    lichtbedarf,
    kategorie,
    ereignistyp,
    startmonat,
    endmonat,
    start_detail,
    end_detail,
):
    """For any event of an active plant, the rendered Ereignisliste HTML
    contains the plant name as a link to /plant/<id>/edit, the event type,
    and the time range.

    # Feature: chronologische-listen, Property 5: Ereignisse enthalten alle Pflichtfelder und Pflanzen-Link

    **Validates: Requirements 3.2, 8.2**
    """
    sm, em = min(startmonat, endmonat), max(startmonat, endmonat)

    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # Add an active plant
        db.add_plant(
            name=name,
            type=type_,
            variety=None,
            lichtbedarf=lichtbedarf,
            kommentar=None,
            kategorie=kategorie,
        )
        all_plants = db.get_all_plants(include_inactive=True)
        plant_id = all_plants[-1]["id"]

        # Add an event
        db.add_ereignis(plant_id, ereignistyp, sm, em, start_detail, end_detail)

        # Reload app module so it uses the same DB
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            response = client.get("/ereignisse")
            assert response.status_code == 200
            html = response.data.decode("utf-8")

            # Plant name as link to edit page
            expected_link = f'<a href="/plant/{plant_id}/edit">{name}</a>'
            assert expected_link in html, (
                f"Expected link '{expected_link}' in HTML"
            )

            # Event type
            assert ereignistyp in html, (
                f"Expected event type '{ereignistyp}' in HTML"
            )

            # Start month name (from GERMAN_MONTHS)
            start_month_name = GERMAN_MONTHS[sm]
            assert start_month_name in html, (
                f"Expected start month name '{start_month_name}' in HTML"
            )


# ---------------------------------------------------------------------------
# Property 6: Filter-Kombination auf beiden Listen
# Feature: chronologische-listen, Property 6: Filter-Kombination auf beiden Listen
# ---------------------------------------------------------------------------

# Strategy: optional filter values (None means "not applied")
filter_kategorie_st = st.one_of(st.none(), st.sampled_from(VALID_KATEGORIEN))
filter_ereignistyp_st = st.one_of(st.none(), st.sampled_from(VALID_EREIGNISTYPEN))
filter_monat_st = st.one_of(st.none(), st.integers(min_value=1, max_value=12))


def _apply_filters(entries, kategorie, ereignistyp, monat):
    """Apply the same filter logic as the Flask routes in Python."""
    result = list(entries)
    if kategorie:
        result = [e for e in result if e["kategorie"] == kategorie]
    if ereignistyp:
        result = [e for e in result if e["ereignistyp"] == ereignistyp]
    if monat:
        result = [e for e in result if e["startmonat"] <= monat <= e["endmonat"]]
    return result


def _count_tbody_rows(html):
    """Count <tr> tags inside <tbody>…</tbody>."""
    import re as _re
    tbody_match = _re.search(r"<tbody>(.*?)</tbody>", html, _re.DOTALL)
    if not tbody_match:
        return 0
    return tbody_match.group(1).count("<tr>")


@settings(max_examples=100, deadline=None)
@given(
    plants=st.lists(
        st.tuples(
            plant_name_st,
            plant_type_st,
            lichtbedarf_st,
            st.sampled_from(VALID_KATEGORIEN),  # always a valid kategorie for filter testing
        ),
        min_size=1,
        max_size=4,
    ),
    ereignisse_per_plant=st.lists(ereignis_list_st, min_size=4, max_size=4),
    beobachtungen_per_plant=st.lists(beobachtung_list_st, min_size=4, max_size=4),
    fk=filter_kategorie_st,
    fe=filter_ereignistyp_st,
    fm=filter_monat_st,
)
def test_filter_kombination(plants, ereignisse_per_plant, beobachtungen_per_plant, fk, fe, fm):
    """For any combination of filters (Kategorie, Ereignistyp, Monat) on the
    Beobachtungs- or Ereignisliste, all displayed entries satisfy all active
    filter criteria simultaneously.

    # Feature: chronologische-listen, Property 6: Filter-Kombination auf beiden Listen

    **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 6.2, 6.3, 6.4, 6.5**
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        db_path = os.path.join(tmp_dir, "test.db")
        db = _init_db(db_path)

        # --- Set up data ---
        for i, (name, type_, lichtbedarf, kategorie) in enumerate(plants):
            db.add_plant(
                name=name,
                type=type_,
                variety=None,
                lichtbedarf=lichtbedarf,
                kommentar=None,
                kategorie=kategorie,
            )
            all_plants = db.get_all_plants(include_inactive=True)
            plant_id = all_plants[-1]["id"]

            for ereignistyp, sm, em, sd, ed in ereignisse_per_plant[i % len(ereignisse_per_plant)]:
                s, e = min(sm, em), max(sm, em)
                db.add_ereignis(plant_id, ereignistyp, s, e, sd, ed)

            for jahr, ereignistyp, sm, em, sd, ed in beobachtungen_per_plant[i % len(beobachtungen_per_plant)]:
                s, e = min(sm, em), max(sm, em)
                db.add_beobachtung(plant_id, jahr, ereignistyp, s, e, None, None, sd, ed)

        # --- Get expected results from DB + Python filter ---
        all_beobachtungen = db.get_all_beobachtungen()
        all_ereignisse = db.get_all_ereignisse()

        expected_beob = _apply_filters(all_beobachtungen, fk, fe, fm)
        expected_ereig = _apply_filters(all_ereignisse, fk, fe, fm)

        # --- Build query params ---
        params = {}
        if fk:
            params["kategorie"] = fk
        if fe:
            params["ereignis"] = fe
        if fm:
            params["monat"] = str(fm)

        # --- Reload app and test via Flask client ---
        import app as app_module
        importlib.reload(app_module)
        app_module.app.config["TESTING"] = True

        with app_module.app.test_client() as client:
            # --- Beobachtungen route ---
            resp_b = client.get("/beobachtungen", query_string=params)
            assert resp_b.status_code == 200
            html_b = resp_b.data.decode("utf-8")
            row_count_b = _count_tbody_rows(html_b)

            assert row_count_b == len(expected_beob), (
                f"Beobachtungen: expected {len(expected_beob)} rows, got {row_count_b}. "
                f"Filters: kategorie={fk!r}, ereignis={fe!r}, monat={fm!r}"
            )

            # Verify each expected entry appears in the HTML
            for b in expected_beob:
                assert b["plant_name"] in html_b, (
                    f"Expected plant name '{b['plant_name']}' in beobachtungen HTML"
                )

            # --- Ereignisse route ---
            resp_e = client.get("/ereignisse", query_string=params)
            assert resp_e.status_code == 200
            html_e = resp_e.data.decode("utf-8")
            row_count_e = _count_tbody_rows(html_e)

            assert row_count_e == len(expected_ereig), (
                f"Ereignisse: expected {len(expected_ereig)} rows, got {row_count_e}. "
                f"Filters: kategorie={fk!r}, ereignis={fe!r}, monat={fm!r}"
            )

            for e in expected_ereig:
                assert e["plant_name"] in html_e, (
                    f"Expected plant name '{e['plant_name']}' in ereignisse HTML"
                )
