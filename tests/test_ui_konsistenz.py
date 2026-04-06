"""Example-based tests for UI-Konsistenz-Verbesserungen (Task 3.5)."""
import importlib
import os

import pytest


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
def client(setup_db, monkeypatch):
    """Flask test client with isolated DB."""
    import app as app_module
    importlib.reload(app_module)
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


@pytest.fixture()
def plant_with_color(setup_db):
    """Create a plant with farbe=#ff0000, return its id."""
    setup_db.add_plant(name="Tomate", type="Gemüse", variety=None,
                       lichtbedarf="Sonne", kommentar=None,
                       kategorie="Gemüse", farbe="#ff0000")
    plants = setup_db.get_all_plants()
    return plants[-1]["id"]


@pytest.fixture()
def plant_without_color(setup_db):
    """Create a plant without farbe, return its id."""
    setup_db.add_plant(name="Basilikum", type="Kräuter", variety=None,
                       lichtbedarf="Halbschatten", kommentar=None,
                       kategorie="Kräuter", farbe=None)
    plants = setup_db.get_all_plants()
    return plants[-1]["id"]


# ---------------------------------------------------------------------------
# 1. Color dot in /beobachtungen when plant has a color (Req 1.1)
# ---------------------------------------------------------------------------

def test_color_dot_in_beobachtungen(client, setup_db, plant_with_color):
    """GET /beobachtungen with a colored plant → HTML contains color-dot with correct color.

    Requirements: 1.1
    """
    setup_db.add_beobachtung(plant_with_color, 2024, "Blüte", 3, 5)
    response = client.get("/beobachtungen")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'class="color-dot"' in html
    assert 'style="background:#ff0000"' in html


# ---------------------------------------------------------------------------
# 2. Color dot in /ereignisse when plant has a color (Req 1.2)
# ---------------------------------------------------------------------------

def test_color_dot_in_ereignisse(client, setup_db, plant_with_color):
    """GET /ereignisse with a colored plant → HTML contains color-dot with correct color.

    Requirements: 1.2
    """
    setup_db.add_ereignis(plant_with_color, "Ernte", 6, 8)
    response = client.get("/ereignisse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'class="color-dot"' in html
    assert 'style="background:#ff0000"' in html


# ---------------------------------------------------------------------------
# 3. No color dot when plant has no color (Req 1.4)
# ---------------------------------------------------------------------------

def test_no_color_dot_without_farbe_beobachtungen(client, setup_db, plant_without_color):
    """GET /beobachtungen with a colorless plant → no color-dot in HTML.

    Requirements: 1.4
    """
    setup_db.add_beobachtung(plant_without_color, 2024, "Ernte", 7, 9)
    response = client.get("/beobachtungen")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Basilikum" in html
    assert 'color-dot' not in html


def test_no_color_dot_without_farbe_ereignisse(client, setup_db, plant_without_color):
    """GET /ereignisse with a colorless plant → no color-dot in HTML.

    Requirements: 1.4
    """
    setup_db.add_ereignis(plant_without_color, "Düngen", 4, 4)
    response = client.get("/ereignisse")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Basilikum" in html
    assert 'color-dot' not in html


# ---------------------------------------------------------------------------
# 4. Plant name on homepage is a link to /plant/<id>/edit (Req 2.1)
# ---------------------------------------------------------------------------

def test_plant_name_is_link_on_homepage(client, plant_with_color):
    """GET / → plant name wrapped in <a href="/plant/<id>/edit">.

    Requirements: 2.1
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert f'href="/plant/{plant_with_color}/edit"' in html
    # The plant name should appear as a link (inside an <a> tag)
    assert f'<a href="/plant/{plant_with_color}/edit">' in html
    assert "Tomate" in html


# ---------------------------------------------------------------------------
# 5. Color dot and name in the same <a> tag (Req 2.2)
# ---------------------------------------------------------------------------

def test_color_dot_and_name_in_same_link(client, plant_with_color):
    """GET / → color-dot span and plant name are inside the same <a> tag.

    Requirements: 2.2
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    # Find the <a> tag that links to the plant edit page and check it contains both
    link_start = html.find(f'<a href="/plant/{plant_with_color}/edit">')
    assert link_start != -1, "Link to plant edit page not found"
    link_end = html.find("</a>", link_start)
    link_content = html[link_start:link_end]
    assert 'class="color-dot"' in link_content
    assert "Tomate" in link_content


# ---------------------------------------------------------------------------
# 6. Edit button (✏️) still in action column (Req 2.3)
# ---------------------------------------------------------------------------

def test_edit_button_still_present(client, plant_with_color):
    """GET / → ✏️ edit button link still exists in the response.

    Requirements: 2.3
    """
    response = client.get("/")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    # The edit button should be in the action-cell div
    assert 'class="action-cell"' in html
    assert "✏️" in html
    # The action cell should contain a link to the edit page
    action_start = html.find('class="action-cell"')
    assert action_start != -1
    action_end = html.find("</div>", action_start)
    action_content = html[action_start:action_end]
    assert f'/plant/{plant_with_color}/edit' in action_content
    assert "✏️" in action_content


# ---------------------------------------------------------------------------
# 7. Ereignis-Formular auf Tagebuchseite vorhanden (Req 3.1)
# ---------------------------------------------------------------------------

def test_ereignis_form_present_on_beobachtungen(client):
    """GET /beobachtungen → contains the Beobachtung form posting to /beobachtung/add.

    Requirements: 3.1
    """
    response = client.get("/beobachtungen")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert 'action="/beobachtung/add"' in html
    assert "Beobachtung hinzufügen" in html


# ---------------------------------------------------------------------------
# 8. Formular enthält alle erwarteten Felder (Req 3.3)
# ---------------------------------------------------------------------------

def test_ereignis_form_contains_expected_fields(client):
    """GET /beobachtungen → Ereignis form has plant_id, ereignistyp, startmonat, endmonat, start_detail, end_detail.

    Requirements: 3.3
    """
    response = client.get("/beobachtungen")
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    # plant_id select
    assert 'name="plant_id"' in html
    # ereignistyp select
    assert 'name="ereignistyp"' in html
    # startmonat select
    assert 'name="startmonat"' in html
    # endmonat select
    assert 'name="endmonat"' in html
    # start_detail select
    assert 'name="start_detail"' in html
    # end_detail select
    assert 'name="end_detail"' in html


# ---------------------------------------------------------------------------
# 9. Fehlermeldung bei fehlender Pflanze (Req 3.6)
# ---------------------------------------------------------------------------

def test_error_when_no_plant_selected(client):
    """POST /beobachtung/add without plant_id → 400 with 'Bitte eine Pflanze auswählen.'

    Requirements: 3.6
    """
    response = client.post("/beobachtung/add", data={
        "ereignistyp": "Ernte",
        "jahr": "2026",
        "startmonat": "6",
        "endmonat": "8",
    })
    assert response.status_code == 400
    html = response.data.decode("utf-8")
    assert "Bitte eine Pflanze auswählen." in html
