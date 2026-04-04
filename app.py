import logging
import os
import sys
from datetime import date

from flask import Flask, abort, redirect, render_template, request, url_for

from db import (add_ereignis, add_plant, get_all_plants, get_plant,
                init_db, remove_ereignis, remove_plant, update_plant,
                add_beobachtung, remove_beobachtung)

PORT = int(os.environ.get("PORT", 5000))

GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

VALID_LICHTBEDARF = {"Sonne", "Halbschatten", "Schatten"}
VALID_EREIGNISTYPEN = {"Blüte", "Ernte", "Düngen", "Rückschnitt"}
VALID_LEBENSDAUER = {"Einjährig", "Zweijährig", "Mehrjährig"}
VALID_KATEGORIEN = ["Obst", "Gemüse", "Kräuter", "Stauden", "Sträucher", "Bäume", "Blumen", "Gründüngung"]

app = Flask(__name__)

try:
    init_db()
except Exception as e:
    logging.error(f"Datenbankfehler beim Start: {e}")
    sys.exit(1)


def _safe_next(next_url: str) -> str:
    """Return next_url only if it's a safe internal path, else '/'."""
    if next_url and (next_url == "/" or next_url.startswith("/plant/")):
        return next_url
    return url_for("index")


@app.route("/")
def index():
    plants = get_all_plants()
    return render_template("index.html", plants=plants, german_months=GERMAN_MONTHS, valid_kategorien=VALID_KATEGORIEN)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    plant_type = request.form.get("type", "").strip() or None
    kategorie = request.form.get("kategorie", "").strip()
    variety = request.form.get("variety", "").strip() or None
    lichtbedarf = request.form.get("lichtbedarf", "").strip()
    kommentar = request.form.get("kommentar", "").strip() or None
    lebensdauer = request.form.get("lebensdauer", "").strip() or None
    try:
        pflanzmonat = int(request.form.get("pflanzmonat", "")) if request.form.get("pflanzmonat") else None
        pflanzjahr = int(request.form.get("pflanzjahr", "")) if request.form.get("pflanzjahr") else None
    except ValueError:
        pflanzmonat = None
        pflanzjahr = None

    if not name:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                valid_kategorien=VALID_KATEGORIEN,
                error="Name darf nicht leer sein.",
            ),
            400,
        )

    if kategorie not in VALID_KATEGORIEN:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                valid_kategorien=VALID_KATEGORIEN,
                error="Bitte eine gültige Kategorie wählen.",
            ),
            400,
        )

    if lichtbedarf not in VALID_LICHTBEDARF:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                valid_kategorien=VALID_KATEGORIEN,
                error="Lichtbedarf muss Sonne, Halbschatten oder Schatten sein.",
            ),
            400,
        )

    add_plant(name, plant_type or "", variety, lichtbedarf, kommentar, lebensdauer, pflanzmonat, pflanzjahr,
              int(request.form.get("anzahl", 1) or 1), kategorie)
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/edit", methods=["GET"])
def edit_route(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)
    return render_template(
        "edit.html",
        plant=plant,
        german_months=GERMAN_MONTHS,
        valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
        valid_lebensdauer=sorted(VALID_LEBENSDAUER),
        valid_kategorien=VALID_KATEGORIEN,
        now_year=date.today().year,
    )


@app.route("/plant/<int:plant_id>/edit", methods=["POST"])
def edit_save(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)

    name = request.form.get("name", "").strip()
    plant_type = request.form.get("type", "").strip() or None
    kategorie = request.form.get("kategorie", "").strip()
    variety = request.form.get("variety", "").strip() or None
    lichtbedarf = request.form.get("lichtbedarf", "").strip()
    kommentar = request.form.get("kommentar", "").strip() or None
    lebensdauer = request.form.get("lebensdauer", "").strip() or None
    try:
        pflanzmonat = int(request.form.get("pflanzmonat", "")) if request.form.get("pflanzmonat") else None
        pflanzjahr = int(request.form.get("pflanzjahr", "")) if request.form.get("pflanzjahr") else None
    except ValueError:
        pflanzmonat = None
        pflanzjahr = None

    if not name:
        return (
            render_template(
                "edit.html",
                plant=plant,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                valid_kategorien=VALID_KATEGORIEN,
                error="Name darf nicht leer sein.",
            ),
            400,
        )

    if kategorie not in VALID_KATEGORIEN:
        return (
            render_template(
                "edit.html",
                plant=plant,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                valid_kategorien=VALID_KATEGORIEN,
                error="Bitte eine gültige Kategorie wählen.",
            ),
            400,
        )

    if lichtbedarf not in VALID_LICHTBEDARF:
        return (
            render_template(
                "edit.html",
                plant=plant,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                valid_kategorien=VALID_KATEGORIEN,
                error="Lichtbedarf muss Sonne, Halbschatten oder Schatten sein.",
            ),
            400,
        )

    update_plant(plant_id, name, plant_type or "", variety, lichtbedarf, kommentar, lebensdauer, pflanzmonat, pflanzjahr,
                 int(request.form.get("anzahl", 1) or 1), kategorie,
                 request.form.get("beschreibung", "").strip() or None)
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/ereignis/add", methods=["POST"])
def add_ereignis_route(plant_id: int):
    ereignistyp = request.form.get("ereignistyp", "").strip()
    next_url = _safe_next(request.form.get("next", ""))

    try:
        startmonat = int(request.form.get("startmonat", ""))
        endmonat = int(request.form.get("endmonat", ""))
    except (ValueError, TypeError):
        plant = get_plant(plant_id)
        return (
            render_template(
                "edit.html" if "/plant/" in next_url else "index.html",
                plant=plant,
                plants=get_all_plants() if "/plant/" not in next_url else None,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                error="Monat muss zwischen 1 und 12 liegen.",
            ),
            400,
        )

    if ereignistyp not in VALID_EREIGNISTYPEN:
        plant = get_plant(plant_id)
        return (
            render_template(
                "edit.html" if "/plant/" in next_url else "index.html",
                plant=plant,
                plants=get_all_plants() if "/plant/" not in next_url else None,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                error="Ereignistyp ungültig.",
            ),
            400,
        )

    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        plant = get_plant(plant_id)
        return (
            render_template(
                "edit.html" if "/plant/" in next_url else "index.html",
                plant=plant,
                plants=get_all_plants() if "/plant/" not in next_url else None,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                error="Monat muss zwischen 1 und 12 liegen.",
            ),
            400,
        )

    if startmonat > endmonat:
        plant = get_plant(plant_id)
        return (
            render_template(
                "edit.html" if "/plant/" in next_url else "index.html",
                plant=plant,
                plants=get_all_plants() if "/plant/" not in next_url else None,
                german_months=GERMAN_MONTHS,
                valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                error="Startmonat darf nicht größer als Endmonat sein.",
            ),
            400,
        )

    add_ereignis(plant_id, ereignistyp, startmonat, endmonat)
    return redirect(next_url)


@app.route("/ereignis/<int:ereignis_id>/remove", methods=["POST"])
def remove_ereignis_route(ereignis_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    remove_ereignis(ereignis_id)
    return redirect(next_url)


@app.route("/remove/<int:id>", methods=["POST"])
def remove(id: int):
    remove_plant(id)
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/beobachtung/add", methods=["POST"])
def add_beobachtung_route(plant_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    ereignistyp = request.form.get("ereignistyp", "").strip()
    phaenologische_phase = request.form.get("phaenologische_phase", "").strip() or None
    notiz = request.form.get("notiz", "").strip() or None

    try:
        jahr = int(request.form.get("jahr", ""))
        startmonat = int(request.form.get("startmonat", ""))
        endmonat = int(request.form.get("endmonat", ""))
    except (ValueError, TypeError):
        plant = get_plant(plant_id)
        return render_template("edit.html", plant=plant, german_months=GERMAN_MONTHS,
                               valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                               valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                               error="Ungültige Eingabe für Jahr oder Monat."), 400

    if ereignistyp not in VALID_EREIGNISTYPEN:
        plant = get_plant(plant_id)
        return render_template("edit.html", plant=plant, german_months=GERMAN_MONTHS,
                               valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                               valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                               error="Ereignistyp ungültig."), 400

    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        plant = get_plant(plant_id)
        return render_template("edit.html", plant=plant, german_months=GERMAN_MONTHS,
                               valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                               valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                               error="Monat muss zwischen 1 und 12 liegen."), 400

    if startmonat > endmonat:
        plant = get_plant(plant_id)
        return render_template("edit.html", plant=plant, german_months=GERMAN_MONTHS,
                               valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                               valid_lebensdauer=sorted(VALID_LEBENSDAUER),
                               error="Startmonat darf nicht größer als Endmonat sein."), 400

    add_beobachtung(plant_id, jahr, ereignistyp, startmonat, endmonat,
                    phaenologische_phase, notiz)
    return redirect(next_url)


@app.route("/beobachtung/<int:beobachtung_id>/remove", methods=["POST"])
def remove_beobachtung_route(beobachtung_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    remove_beobachtung(beobachtung_id)
    return redirect(next_url)
