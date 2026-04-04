import logging
import os
import sys

from flask import Flask, redirect, render_template, request, url_for

from db import add_ereignis, add_plant, get_all_plants, init_db, remove_ereignis, remove_plant

PORT = int(os.environ.get("PORT", 5000))

GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

VALID_LICHTBEDARF = {"Sonne", "Halbschatten", "Schatten"}
VALID_EREIGNISTYPEN = {"Blüte", "Ernte", "Düngen", "Rückschnitt"}

app = Flask(__name__)

try:
    init_db()
except Exception as e:
    logging.error(f"Datenbankfehler beim Start: {e}")
    sys.exit(1)


@app.route("/")
def index():
    plants = get_all_plants()
    return render_template("index.html", plants=plants, german_months=GERMAN_MONTHS)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    plant_type = request.form.get("type", "").strip()
    variety = request.form.get("variety", "").strip() or None
    lichtbedarf = request.form.get("lichtbedarf", "").strip()
    kommentar = request.form.get("kommentar", "").strip() or None

    if not name or not plant_type:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                error="Name und Typ dürfen nicht leer sein.",
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
                error="Lichtbedarf muss Sonne, Halbschatten oder Schatten sein.",
            ),
            400,
        )

    add_plant(name, plant_type, variety, lichtbedarf, kommentar)
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/ereignis/add", methods=["POST"])
def add_ereignis_route(plant_id: int):
    ereignistyp = request.form.get("ereignistyp", "").strip()

    try:
        startmonat = int(request.form.get("startmonat", ""))
        endmonat = int(request.form.get("endmonat", ""))
    except (ValueError, TypeError):
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                error="Monat muss zwischen 1 und 12 liegen.",
            ),
            400,
        )

    if ereignistyp not in VALID_EREIGNISTYPEN:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                error="Ereignistyp ungültig.",
            ),
            400,
        )

    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                error="Monat muss zwischen 1 und 12 liegen.",
            ),
            400,
        )

    if startmonat > endmonat:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                german_months=GERMAN_MONTHS,
                error="Startmonat darf nicht größer als Endmonat sein.",
            ),
            400,
        )

    add_ereignis(plant_id, ereignistyp, startmonat, endmonat)
    return redirect(url_for("index"))


@app.route("/ereignis/<int:ereignis_id>/remove", methods=["POST"])
def remove_ereignis_route(ereignis_id: int):
    remove_ereignis(ereignis_id)
    return redirect(url_for("index"))


@app.route("/remove/<int:id>", methods=["POST"])
def remove(id: int):
    remove_plant(id)
    return redirect(url_for("index"))
