import logging
import os
import sys

from flask import Flask, redirect, render_template, request, url_for

from db import add_plant, get_all_plants, init_db, remove_plant

PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

try:
    init_db()
except Exception as e:
    logging.error(f"Datenbankfehler beim Start: {e}")
    sys.exit(1)


@app.route("/")
def index():
    plants = get_all_plants()
    return render_template("index.html", plants=plants)


@app.route("/add", methods=["POST"])
def add():
    name = request.form.get("name", "").strip()
    plant_type = request.form.get("type", "").strip()
    variety = request.form.get("variety", "").strip() or None

    if not name or not plant_type:
        plants = get_all_plants()
        return (
            render_template(
                "index.html",
                plants=plants,
                error="Name und Typ dürfen nicht leer sein.",
            ),
            400,
        )

    add_plant(name, plant_type, variety)
    return redirect(url_for("index"))


@app.route("/remove/<int:id>", methods=["POST"])
def remove(id: int):
    remove_plant(id)
    return redirect(url_for("index"))
