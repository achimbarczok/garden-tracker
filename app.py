import json
import logging
import os
import re
import sys
import uuid
from datetime import date
from io import BytesIO
from pathlib import Path

from flask import Flask, abort, jsonify, redirect, render_template, request, send_from_directory, url_for
from PIL import Image, ImageOps

from llm import get_provider, is_llm_configured

from db import (add_ereignis, add_plant, get_all_plants, get_plant,
                init_db, close_db, remove_ereignis, remove_plant, update_plant,
                update_ereignis, update_beobachtung,
                add_beobachtung, remove_beobachtung,
                get_phaenologie_jahr, get_phaenologie_alle_jahre,
                upsert_phaenologie, remove_phaenologie, get_aktuelle_phase,
                duplicate_plant, set_plant_active,
                get_all_beobachtungen, get_all_ereignisse, berechne_sortierwert,
                add_foto, get_foto, remove_foto, set_hauptbild, count_fotos,
                get_fotos_by_plant_id,
                get_kartenbild, save_kartenbild, remove_kartenbild,
                get_kartenpositionen, add_kartenposition, remove_kartenposition,
                PHAENOLOGISCHE_PHASEN, PHASEN_ICONS)

PORT = int(os.environ.get("PORT", 5000))

GERMAN_MONTHS = {
    1: "Januar", 2: "Februar", 3: "März", 4: "April",
    5: "Mai", 6: "Juni", 7: "Juli", 8: "August",
    9: "September", 10: "Oktober", 11: "November", 12: "Dezember",
}

VALID_LICHTBEDARF = {"Sonne", "Halbschatten", "Schatten"}
VALID_EREIGNISTYPEN = {"Blüte", "Ernte", "Düngen", "Rückschnitt", "Vorkultur", "Auspflanzen", "Direktsaat", "Pflege"}
ZEITRAUM_EREIGNISTYPEN = {"Blüte", "Ernte"}
VALID_LEBENSDAUER = {"Einjährig", "Zweijährig", "Mehrjährig"}
VALID_KATEGORIEN = ["Obst", "Gemüse", "Kräuter", "Stauden", "Gehölze", "Blumen", "Gründüngung", "Gartenpflege"]
VALID_DETAIL = {"", "Anfang", "Mitte", "Ende"}

MAX_FOTO_SIZE = 10 * 1024 * 1024  # 10 MB
MAX_FOTOS_PER_PLANT = 5
MAX_FOTO_DIMENSION = 640
FOTOS_DIR = Path(os.environ.get("DB_PATH", "/data/plants.db")).parent / "fotos"
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png"}

MAX_KARTE_DIMENSION = 1920
KARTE_DIR = Path(os.environ.get("DB_PATH", "/data/plants.db")).parent / "karte"

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_FOTO_SIZE
app.teardown_appcontext(close_db)

try:
    init_db()
except Exception as e:
    logging.error(f"Datenbankfehler beim Start: {e}")
    sys.exit(1)

os.makedirs(FOTOS_DIR, exist_ok=True)
os.makedirs(KARTE_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_next(next_url: str) -> str:
    """Return next_url only if it's a safe internal path, else '/'."""
    if next_url and (next_url == "/" or next_url.startswith("/plant/")
                    or next_url.startswith("/phaenologie")
                    or next_url.startswith("/beobachtungen")
                    or next_url.startswith("/ereignisse")
                    or next_url.startswith("/gartenkarte")):
        return next_url
    return url_for("index")


def _render_index_error(error: str):
    """Render index.html with an error message and HTTP 400."""
    plants = get_all_plants()
    return (
        render_template(
            "index.html",
            plants=plants,
            german_months=GERMAN_MONTHS,
            valid_kategorien=VALID_KATEGORIEN,
            valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
            filter_kategorie="",
            filter_ereignis="",
            filter_monat="",
            show_inactive="",
            aktuelle_phase=None,
            phasen_icons=PHASEN_ICONS,
            error=error,
            llm_available=is_llm_configured(),
        ),
        400,
    )


def _render_edit_error(plant: dict, error: str):
    """Render edit.html with an error message and HTTP 400."""
    return (
        render_template(
            "edit.html",
            plant=plant,
            german_months=GERMAN_MONTHS,
            valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
            zeitraum_ereignistypen=sorted(ZEITRAUM_EREIGNISTYPEN),
            valid_lebensdauer=sorted(VALID_LEBENSDAUER),
            valid_kategorien=VALID_KATEGORIEN,
            now_year=date.today().year,
            max_fotos=MAX_FOTOS_PER_PLANT,
            error=error,
            llm_available=is_llm_configured(),
        ),
        400,
    )


def _render_karte_error(error, kartenbild=None, positionen=None, plants=None):
    """Render gartenkarte.html with an error message and HTTP 400."""
    if kartenbild is None:
        kartenbild = get_kartenbild()
    if positionen is None:
        positionen = get_kartenpositionen()
    if plants is None:
        plants = get_all_plants()
    return (
        render_template("gartenkarte.html", error=error,
                        kartenbild=kartenbild, positionen=positionen, plants=plants),
        400,
    )


def _render_beobachtungen_error(error: str):
    """Render beobachtungen.html with an error message and HTTP 400."""
    beobachtungen = get_all_beobachtungen()
    plants = get_all_plants()
    return (
        render_template(
            "beobachtungen.html",
            beobachtungen=beobachtungen,
            plants=plants,
            german_months=GERMAN_MONTHS,
            valid_kategorien=VALID_KATEGORIEN,
            valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
            zeitraum_ereignistypen=sorted(ZEITRAUM_EREIGNISTYPEN),
            filter_kategorie="",
            filter_ereignis="",
            filter_monat="",
            now_year=date.today().year,
            error=error,
        ),
        400,
    )


def _process_image(file_storage, max_dimension: int) -> bytes:
    """Process uploaded image: EXIF transpose, resize to max_dimension, convert to JPEG."""
    img = Image.open(file_storage)
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    if max(img.size) > max_dimension:
        img.thumbnail((max_dimension, max_dimension), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def process_image(file_storage) -> bytes:
    """Process uploaded plant photo: EXIF transpose, resize to max 640px, JPEG."""
    return _process_image(file_storage, MAX_FOTO_DIMENSION)


def process_kartenbild(file_storage) -> bytes:
    """Process uploaded garden map image: EXIF transpose, resize to max 1920px, JPEG."""
    return _process_image(file_storage, MAX_KARTE_DIMENSION)


def _parse_plant_form():
    """Parse and validate common plant form fields. Returns (data, error)."""
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
        return None, "Name darf nicht leer sein."
    if kategorie not in VALID_KATEGORIEN:
        return None, "Bitte eine gültige Kategorie wählen."
    if lichtbedarf not in VALID_LICHTBEDARF:
        return None, "Lichtbedarf muss Sonne, Halbschatten oder Schatten sein."

    farbe_raw = request.form.get("farbe", "").strip()
    farbe = farbe_raw if farbe_raw and farbe_raw != "#000000" else None

    return {
        "name": name, "type": plant_type or "", "variety": variety,
        "lichtbedarf": lichtbedarf, "kommentar": kommentar,
        "lebensdauer": lebensdauer, "pflanzmonat": pflanzmonat,
        "pflanzjahr": pflanzjahr,
        "kategorie": kategorie,
        "beschreibung": request.form.get("beschreibung", "").strip() or None,
        "farbe": farbe,
    }, None


@app.route("/")
def index():
    show_inactive = request.args.get("show_inactive", "")
    plants = get_all_plants(include_inactive=bool(show_inactive))

    # Filter: Kategorie
    filter_kategorie = request.args.get("kategorie", "")
    if filter_kategorie:
        plants = [p for p in plants if p.get("kategorie") == filter_kategorie]

    # Filter: Ereignistyp + Monat
    filter_ereignis = request.args.get("ereignis", "")
    filter_monat = request.args.get("monat", "")
    if filter_monat:
        try:
            fm = int(filter_monat)
        except ValueError:
            fm = None
        if fm and 1 <= fm <= 12:
            def hat_ereignis_im_monat(plant):
                for e in plant.get("ereignisse", []):
                    if filter_ereignis and e["ereignistyp"] != filter_ereignis:
                        continue
                    if e["startmonat"] <= fm <= e["endmonat"]:
                        return True
                return False
            plants = [p for p in plants if hat_ereignis_im_monat(p)]
        elif filter_ereignis:
            plants = [p for p in plants
                      if any(e["ereignistyp"] == filter_ereignis for e in p.get("ereignisse", []))]
    elif filter_ereignis:
        plants = [p for p in plants
                  if any(e["ereignistyp"] == filter_ereignis for e in p.get("ereignisse", []))]

    heute = date.today()
    aktuelle_phase = get_aktuelle_phase(heute.month, heute.day, heute.year)

    return render_template("index.html", plants=plants, german_months=GERMAN_MONTHS,
                           valid_kategorien=VALID_KATEGORIEN,
                           valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                           filter_kategorie=filter_kategorie,
                           filter_ereignis=filter_ereignis,
                           filter_monat=filter_monat,
                           show_inactive=show_inactive,
                           aktuelle_phase=aktuelle_phase,
                           phasen_icons=PHASEN_ICONS,
                           llm_available=is_llm_configured())


@app.route("/add", methods=["POST"])
def add():
    data, error = _parse_plant_form()
    if error:
        return _render_index_error(error)

    new_id = add_plant(data["name"], data["type"], data["variety"], data["lichtbedarf"],
              data["kommentar"], data["lebensdauer"], data["pflanzmonat"],
              data["pflanzjahr"], 1, data["kategorie"],
              beschreibung=data["beschreibung"], farbe=data["farbe"])
    return redirect(f"/plant/{new_id}/edit")


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
        zeitraum_ereignistypen=sorted(ZEITRAUM_EREIGNISTYPEN),
        valid_lebensdauer=sorted(VALID_LEBENSDAUER),
        valid_kategorien=VALID_KATEGORIEN,
        now_year=date.today().year,
        max_fotos=MAX_FOTOS_PER_PLANT,
        llm_available=is_llm_configured(),
    )


@app.route("/plant/<int:plant_id>/edit", methods=["POST"])
def edit_save(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)

    data, error = _parse_plant_form()
    if error:
        return _render_edit_error(plant, error)

    update_plant(plant_id, data["name"], data["type"], data["variety"],
                 data["lichtbedarf"], data["kommentar"], data["lebensdauer"],
                 data["pflanzmonat"], data["pflanzjahr"], 1,
                 data["kategorie"], data["beschreibung"], data["farbe"])
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/ereignis/add", methods=["POST"])
def add_ereignis_route(plant_id: int):
    ereignistyp = request.form.get("ereignistyp", "").strip()
    next_url = _safe_next(request.form.get("next", ""))

    try:
        startmonat = int(request.form.get("startmonat", ""))
        endmonat = int(request.form.get("endmonat", ""))
    except (ValueError, TypeError):
        if "/plant/" in next_url:
            plant = get_plant(plant_id)
            return _render_edit_error(plant, "Monat muss zwischen 1 und 12 liegen.")
        return _render_index_error("Monat muss zwischen 1 und 12 liegen.")

    if ereignistyp not in VALID_EREIGNISTYPEN:
        if "/plant/" in next_url:
            plant = get_plant(plant_id)
            return _render_edit_error(plant, "Ereignistyp ungültig.")
        return _render_index_error("Ereignistyp ungültig.")

    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        if "/plant/" in next_url:
            plant = get_plant(plant_id)
            return _render_edit_error(plant, "Monat muss zwischen 1 und 12 liegen.")
        return _render_index_error("Monat muss zwischen 1 und 12 liegen.")

    start_detail = request.form.get("start_detail", "").strip() or None
    if ereignistyp in ZEITRAUM_EREIGNISTYPEN:
        end_detail = request.form.get("end_detail", "").strip() or None
        if startmonat > endmonat:
            if "/plant/" in next_url:
                plant = get_plant(plant_id)
                return _render_edit_error(plant, "Startmonat darf nicht größer als Endmonat sein.")
            return _render_index_error("Startmonat darf nicht größer als Endmonat sein.")
    else:
        endmonat = startmonat
        end_detail = start_detail

    add_ereignis(plant_id, ereignistyp, startmonat, endmonat,
                 start_detail, end_detail)
    return redirect(next_url)


@app.route("/beobachtung/add", methods=["POST"])
def add_beobachtung_from_beobachtungen():
    # 1. Read and validate plant_id
    plant_id_raw = request.form.get("plant_id", "").strip()
    if not plant_id_raw:
        return _render_beobachtungen_error("Bitte eine Pflanze auswählen.")

    try:
        plant_id = int(plant_id_raw)
    except (ValueError, TypeError):
        return _render_beobachtungen_error("Pflanze nicht gefunden.")

    # 2. Look up plant, check exists and active
    plant = get_plant(plant_id)
    if plant is None or not plant.get("aktiv"):
        return _render_beobachtungen_error("Pflanze nicht gefunden.")

    # 3. Validate ereignistyp
    ereignistyp = request.form.get("ereignistyp", "").strip()
    if ereignistyp not in VALID_EREIGNISTYPEN:
        return _render_beobachtungen_error("Ereignistyp ungültig.")

    # 4. Validate jahr
    try:
        jahr = int(request.form.get("jahr", ""))
    except (ValueError, TypeError):
        return _render_beobachtungen_error("Ungültige Eingabe für Jahr.")

    # 5. Validate startmonat
    try:
        startmonat = int(request.form.get("startmonat", ""))
    except (ValueError, TypeError):
        return _render_beobachtungen_error("Monat muss zwischen 1 und 12 liegen.")

    if not (1 <= startmonat <= 12):
        return _render_beobachtungen_error("Monat muss zwischen 1 und 12 liegen.")

    start_detail = request.form.get("start_detail", "").strip() or None
    notiz = request.form.get("notiz", "").strip() or None

    # 6. Period vs non-period handling
    if ereignistyp in ZEITRAUM_EREIGNISTYPEN:
        try:
            endmonat = int(request.form.get("endmonat", ""))
        except (ValueError, TypeError):
            return _render_beobachtungen_error("Monat muss zwischen 1 und 12 liegen.")

        if not (1 <= endmonat <= 12):
            return _render_beobachtungen_error("Monat muss zwischen 1 und 12 liegen.")

        if startmonat > endmonat:
            return _render_beobachtungen_error("Startmonat darf nicht größer als Endmonat sein.")

        end_detail = request.form.get("end_detail", "").strip() or None
    else:
        endmonat = startmonat
        end_detail = start_detail

    # 7. Save and redirect
    add_beobachtung(plant_id, jahr, ereignistyp, startmonat, endmonat,
                    notiz=notiz, start_detail=start_detail, end_detail=end_detail)
    return redirect("/beobachtungen")


@app.route("/ereignis/<int:ereignis_id>/remove", methods=["POST"])
def remove_ereignis_route(ereignis_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    remove_ereignis(ereignis_id)
    return redirect(next_url)


@app.route("/ereignis/<int:ereignis_id>/edit", methods=["POST"])
def edit_ereignis_route(ereignis_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    ereignistyp = request.form.get("ereignistyp", "").strip()

    try:
        startmonat = int(request.form.get("startmonat", ""))
        endmonat = int(request.form.get("endmonat", ""))
    except (ValueError, TypeError):
        return redirect(next_url)

    if ereignistyp not in VALID_EREIGNISTYPEN:
        return redirect(next_url)
    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        return redirect(next_url)

    start_detail = request.form.get("start_detail", "").strip() or None
    if ereignistyp in ZEITRAUM_EREIGNISTYPEN:
        if startmonat > endmonat:
            return redirect(next_url)
        end_detail = request.form.get("end_detail", "").strip() or None
    else:
        endmonat = startmonat
        end_detail = start_detail

    update_ereignis(ereignis_id, ereignistyp, startmonat, endmonat,
                    start_detail, end_detail)
    return redirect(next_url)


@app.route("/remove/<int:id>", methods=["POST"])
def remove(id: int):
    remove_plant(id)
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/duplicate", methods=["POST"])
def duplicate_route(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)
    new_id = duplicate_plant(plant_id)
    return redirect(f"/plant/{new_id}/edit")


@app.route("/plant/<int:plant_id>/deactivate", methods=["POST"])
def deactivate_route(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)
    try:
        set_plant_active(plant_id, 0)
    except Exception:
        return redirect(url_for("index"))
    return redirect(url_for("index"))


@app.route("/plant/<int:plant_id>/activate", methods=["POST"])
def activate_route(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)
    try:
        set_plant_active(plant_id, 1)
    except Exception:
        return redirect(url_for("index"))
    return redirect(f"/plant/{plant_id}/edit")


@app.route("/plant/<int:plant_id>/foto/upload", methods=["POST"])
def upload_foto_route(plant_id: int):
    plant = get_plant(plant_id)
    if plant is None:
        abort(404)

    foto = request.files.get("foto")
    if not foto or foto.filename == "":
        return _render_edit_error(plant, "Bitte eine Bilddatei auswählen.")

    if foto.content_type not in ALLOWED_MIME_TYPES:
        return _render_edit_error(plant, "Nur JPEG- und PNG-Dateien sind erlaubt.")

    if count_fotos(plant_id) >= MAX_FOTOS_PER_PLANT:
        return _render_edit_error(plant, f"Maximum von {MAX_FOTOS_PER_PLANT} Fotos erreicht.")

    try:
        data = process_image(foto)
    except Exception:
        return _render_edit_error(plant, "Das Bild konnte nicht verarbeitet werden.")

    dateiname = f"{uuid.uuid4()}.jpg"
    filepath = FOTOS_DIR / dateiname

    ist_hauptbild = 1 if count_fotos(plant_id) == 0 else 0
    bezeichnung = request.form.get("bezeichnung", "").strip() or None

    try:
        filepath.write_bytes(data)
    except OSError:
        return _render_edit_error(plant, "Fehler beim Speichern der Datei.")

    try:
        add_foto(plant_id, dateiname, bezeichnung, ist_hauptbild)
    except Exception:
        try:
            filepath.unlink()
        except OSError:
            pass
        return _render_edit_error(plant, "Fehler beim Speichern in der Datenbank.")

    return redirect(f"/plant/{plant_id}/edit")


@app.route("/foto/<int:foto_id>/remove", methods=["POST"])
def remove_foto_route(foto_id: int):
    foto = get_foto(foto_id)
    if foto is None:
        abort(404)
    plant_id = foto["plant_id"]
    remove_foto(foto_id)
    try:
        (FOTOS_DIR / foto["dateiname"]).unlink()
    except OSError:
        pass
    return redirect(f"/plant/{plant_id}/edit")


@app.route("/foto/<int:foto_id>/hauptbild", methods=["POST"])
def set_hauptbild_route(foto_id: int):
    foto = get_foto(foto_id)
    if foto is None:
        abort(404)
    set_hauptbild(foto_id, foto["plant_id"])
    return redirect(f"/plant/{foto['plant_id']}/edit")


@app.route("/fotos/<path:dateiname>")
def serve_foto(dateiname: str):
    return send_from_directory(str(FOTOS_DIR), dateiname)


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
        return _render_edit_error(plant, "Ungültige Eingabe für Jahr oder Monat.")

    if ereignistyp not in VALID_EREIGNISTYPEN:
        plant = get_plant(plant_id)
        return _render_edit_error(plant, "Ereignistyp ungültig.")

    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        plant = get_plant(plant_id)
        return _render_edit_error(plant, "Monat muss zwischen 1 und 12 liegen.")

    start_detail = request.form.get("start_detail", "").strip() or None
    if ereignistyp in ZEITRAUM_EREIGNISTYPEN:
        end_detail = request.form.get("end_detail", "").strip() or None
        if startmonat > endmonat:
            plant = get_plant(plant_id)
            return _render_edit_error(plant, "Startmonat darf nicht größer als Endmonat sein.")
    else:
        endmonat = startmonat
        end_detail = start_detail

    add_beobachtung(plant_id, jahr, ereignistyp, startmonat, endmonat,
                    phaenologische_phase, notiz,
                    start_detail, end_detail)
    return redirect(next_url)


@app.route("/beobachtung/<int:beobachtung_id>/remove", methods=["POST"])
def remove_beobachtung_route(beobachtung_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    remove_beobachtung(beobachtung_id)
    return redirect(next_url)


@app.route("/beobachtung/<int:beobachtung_id>/edit", methods=["POST"])
def edit_beobachtung_route(beobachtung_id: int):
    next_url = _safe_next(request.form.get("next", ""))
    ereignistyp = request.form.get("ereignistyp", "").strip()
    notiz = request.form.get("notiz", "").strip() or None

    try:
        jahr = int(request.form.get("jahr", ""))
        startmonat = int(request.form.get("startmonat", ""))
        endmonat = int(request.form.get("endmonat", ""))
    except (ValueError, TypeError):
        return redirect(next_url)

    if ereignistyp not in VALID_EREIGNISTYPEN:
        return redirect(next_url)
    if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
        return redirect(next_url)

    start_detail = request.form.get("start_detail", "").strip() or None
    if ereignistyp in ZEITRAUM_EREIGNISTYPEN:
        if startmonat > endmonat:
            return redirect(next_url)
        end_detail = request.form.get("end_detail", "").strip() or None
    else:
        endmonat = startmonat
        end_detail = start_detail

    update_beobachtung(beobachtung_id, jahr, ereignistyp, startmonat, endmonat,
                       request.form.get("phaenologische_phase", "").strip() or None,
                       notiz,
                       start_detail, end_detail)
    return redirect(next_url)


@app.route("/beobachtungen")
def beobachtungen_page():
    beobachtungen = get_all_beobachtungen()

    filter_kategorie = request.args.get("kategorie", "")
    filter_ereignis = request.args.get("ereignis", "")
    filter_monat = request.args.get("monat", "")

    if filter_kategorie:
        beobachtungen = [b for b in beobachtungen if b["kategorie"] == filter_kategorie]
    if filter_ereignis:
        beobachtungen = [b for b in beobachtungen if b["ereignistyp"] == filter_ereignis]
    if filter_monat:
        try:
            fm = int(filter_monat)
        except ValueError:
            fm = None
        if fm and 1 <= fm <= 12:
            beobachtungen = [b for b in beobachtungen if b["startmonat"] <= fm <= b["endmonat"]]

    plants = get_all_plants()

    return render_template("beobachtungen.html",
                           beobachtungen=beobachtungen,
                           plants=plants,
                           german_months=GERMAN_MONTHS,
                           valid_kategorien=VALID_KATEGORIEN,
                           valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                           zeitraum_ereignistypen=sorted(ZEITRAUM_EREIGNISTYPEN),
                           now_year=date.today().year,
                           filter_kategorie=filter_kategorie,
                           filter_ereignis=filter_ereignis,
                           filter_monat=filter_monat)


@app.route("/ereignisse")
def ereignisse_page():
    ereignisse = get_all_ereignisse()

    filter_kategorie = request.args.get("kategorie", "")
    filter_ereignis = request.args.get("ereignis", "")
    filter_monat = request.args.get("monat", "")

    if filter_kategorie:
        ereignisse = [e for e in ereignisse if e["kategorie"] == filter_kategorie]
    if filter_ereignis:
        ereignisse = [e for e in ereignisse if e["ereignistyp"] == filter_ereignis]
    if filter_monat:
        try:
            fm = int(filter_monat)
        except ValueError:
            fm = None
        if fm and 1 <= fm <= 12:
            ereignisse = [e for e in ereignisse if e["startmonat"] <= fm <= e["endmonat"]]

    return render_template("ereignisse.html",
                           ereignisse=ereignisse,
                           german_months=GERMAN_MONTHS,
                           valid_kategorien=VALID_KATEGORIEN,
                           valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                           filter_kategorie=filter_kategorie,
                           filter_ereignis=filter_ereignis,
                           filter_monat=filter_monat)


@app.route("/phaenologie")
def phaenologie_page():
    heute = date.today()
    selected_year = request.args.get("jahr", str(heute.year))
    try:
        selected_year = int(selected_year)
    except ValueError:
        selected_year = heute.year
    phasen = get_phaenologie_jahr(selected_year)
    alle_jahre = get_phaenologie_alle_jahre()
    if selected_year not in alle_jahre:
        alle_jahre = sorted(set(alle_jahre + [selected_year]), reverse=True)
    aktuelle_phase = get_aktuelle_phase(heute.month, heute.day, heute.year)
    return render_template("phaenologie.html",
                           phasen=phasen,
                           alle_phasen=PHAENOLOGISCHE_PHASEN,
                           phasen_icons=PHASEN_ICONS,
                           alle_jahre=alle_jahre,
                           selected_year=selected_year,
                           german_months=GERMAN_MONTHS,
                           aktuelle_phase=aktuelle_phase,
                           now_year=heute.year)


@app.route("/phaenologie/save", methods=["POST"])
def phaenologie_save():
    jahr = int(request.form.get("jahr", date.today().year))
    phase = request.form.get("phase", "").strip()
    if phase not in PHAENOLOGISCHE_PHASEN:
        return redirect(url_for("phaenologie_page", jahr=jahr))
    try:
        startmonat = int(request.form.get("startmonat", ""))
    except (ValueError, TypeError):
        return redirect(url_for("phaenologie_page", jahr=jahr))
    start_detail = request.form.get("start_detail", "").strip() or None
    upsert_phaenologie(jahr, phase, startmonat, start_detail)
    return redirect(url_for("phaenologie_page", jahr=jahr))


@app.route("/phaenologie/<int:phaenologie_id>/remove", methods=["POST"])
def phaenologie_remove(phaenologie_id: int):
    jahr = request.form.get("jahr", str(date.today().year))
    remove_phaenologie(phaenologie_id)
    return redirect(url_for("phaenologie_page", jahr=jahr))


def _filter_plant_ids_by_ereignis(ereignisse, filter_ereignis, filter_monat):
    """Filter events by type and/or month, return set of matching plant_ids."""
    if filter_ereignis:
        ereignisse = [e for e in ereignisse if e["ereignistyp"] == filter_ereignis]
    if filter_monat:
        try:
            fm = int(filter_monat)
        except ValueError:
            fm = None
        if fm and 1 <= fm <= 12:
            ereignisse = [e for e in ereignisse if e["startmonat"] <= fm <= e["endmonat"]]
    return {e["plant_id"] for e in ereignisse}


@app.route("/gartenkarte")
def gartenkarte_page():
    kartenbild = get_kartenbild()
    positionen = get_kartenpositionen()
    plants = get_all_plants()

    # Nur aktive Pflanzen anzeigen
    positionen = [p for p in positionen if p.get("aktiv", 1) == 1]

    filter_kategorie = request.args.get("kategorie", "")
    filter_ereignis = request.args.get("ereignis", "")
    filter_monat = request.args.get("monat", "")

    # Filter: Kategorie
    if filter_kategorie:
        positionen = [p for p in positionen if p.get("kategorie") == filter_kategorie]

    # Filter: Ereignistyp + Monat (benötigt Ereignis-Lookup)
    if filter_ereignis or filter_monat:
        ereignisse = get_all_ereignisse()
        plant_ids_mit_ereignis = _filter_plant_ids_by_ereignis(
            ereignisse, filter_ereignis, filter_monat
        )
        positionen = [p for p in positionen if p["plant_id"] in plant_ids_mit_ereignis]

    return render_template("gartenkarte.html",
                           kartenbild=kartenbild,
                           positionen=positionen,
                           plants=plants,
                           german_months=GERMAN_MONTHS,
                           valid_kategorien=VALID_KATEGORIEN,
                           valid_ereignistypen=sorted(VALID_EREIGNISTYPEN),
                           filter_kategorie=filter_kategorie,
                           filter_ereignis=filter_ereignis,
                           filter_monat=filter_monat)


@app.route("/gartenkarte/bild/upload", methods=["POST"])
def upload_kartenbild():
    bild = request.files.get("bild")
    if not bild or bild.filename == "":
        return _render_karte_error("Bitte eine Bilddatei auswählen.")

    if bild.content_type not in ALLOWED_MIME_TYPES:
        return _render_karte_error("Nur JPEG- und PNG-Dateien sind erlaubt.")

    try:
        data = process_kartenbild(bild)
    except Exception:
        return _render_karte_error("Das Bild konnte nicht verarbeitet werden.")

    # Delete old image file if exists
    old = get_kartenbild()
    if old:
        try:
            (KARTE_DIR / old["dateiname"]).unlink()
        except OSError:
            pass

    dateiname = f"{uuid.uuid4()}.jpg"
    filepath = KARTE_DIR / dateiname

    try:
        filepath.write_bytes(data)
    except OSError:
        return _render_karte_error("Fehler beim Speichern der Datei.")

    save_kartenbild(dateiname)
    return redirect("/gartenkarte")


@app.route("/gartenkarte/bild/remove", methods=["POST"])
def remove_kartenbild_route():
    old = get_kartenbild()
    if not old:
        return redirect("/gartenkarte")
    remove_kartenbild()
    try:
        (KARTE_DIR / old["dateiname"]).unlink()
    except OSError:
        pass
    return redirect("/gartenkarte")


@app.route("/gartenkarte/position/add", methods=["POST"])
def add_position_route():
    if not get_kartenbild():
        return _render_karte_error("Bitte zuerst ein Kartenbild hochladen.")

    try:
        plant_id = int(request.form.get("plant_id", ""))
    except (ValueError, TypeError):
        abort(404)

    plant = get_plant(plant_id)
    if plant is None:
        abort(404)

    try:
        x = float(request.form.get("x", ""))
        y = float(request.form.get("y", ""))
    except (ValueError, TypeError):
        return _render_karte_error("Ungültige Koordinaten.")

    if not (0.0 <= x <= 100.0) or not (0.0 <= y <= 100.0):
        return _render_karte_error("Ungültige Koordinaten.")

    add_kartenposition(plant_id, x, y)
    # Nach dem Platzieren die Pflanzen-Auswahl beibehalten
    selected = request.form.get("selected_plant_id", str(plant_id))
    return redirect(f"/gartenkarte?plant_id={selected}")


@app.route("/gartenkarte/position/<int:position_id>/remove", methods=["POST"])
def remove_position_route(position_id):
    remove_kartenposition(position_id)
    # plant_id aus Referrer oder Form beibehalten
    plant_id = request.form.get("selected_plant_id", "")
    if plant_id:
        return redirect(f"/gartenkarte?plant_id={plant_id}")
    return redirect("/gartenkarte")


@app.route("/karte/<path:dateiname>")
def serve_kartenbild(dateiname):
    return send_from_directory(str(KARTE_DIR), dateiname)


# ---------------------------------------------------------------------------
# KI-Autofill
# ---------------------------------------------------------------------------

def _build_autofill_prompt(name: str) -> str:
    """Erstellt den Prompt für den Autofill-LLM-Aufruf."""
    valid_kategorien_str = ", ".join(VALID_KATEGORIEN)
    valid_lichtbedarf_str = ", ".join(sorted(VALID_LICHTBEDARF))
    valid_lebensdauer_str = ", ".join(sorted(VALID_LEBENSDAUER))
    valid_ereignistypen_str = ", ".join(sorted(VALID_EREIGNISTYPEN))

    return f"""Gib mir strukturierte Pflanzendaten für: {name}

Antworte ausschließlich mit einem JSON-Objekt im folgenden Format (keine zusätzlichen Erklärungen):

{{
  "beschreibung": "Kurze Beschreibung auf Deutsch mit gartenrelevanten Infos (Standort, Pflege, Schnitt)",
  "typ": "Pflanzentyp (z.B. Beerenobst, Laubbaum, Staude)",
  "sorte": "Sortenname oder leer lassen",
  "lichtbedarf": "Einer der Werte: {valid_lichtbedarf_str}",
  "lebensdauer": "Einer der Werte: {valid_lebensdauer_str}",
  "kategorie": "Einer der Werte: {valid_kategorien_str}",
  "ereignisse": [
    {{
      "ereignistyp": "Einer der Werte: {valid_ereignistypen_str}",
      "startmonat": 1,
      "endmonat": 12,
      "start_detail": "",
      "end_detail": ""
    }}
  ]
}}

Regeln:
- Monatswerte als Ganzzahlen von 1 (Januar) bis 12 (Dezember)
- Detail-Werte für start_detail und end_detail: "Anfang", "Mitte", "Ende" oder "" (leer)
- Gültige Werte für lichtbedarf: {valid_lichtbedarf_str}
- Gültige Werte für lebensdauer: {valid_lebensdauer_str}
- Gültige Werte für kategorie: {valid_kategorien_str}
- Gültige Werte für ereignistyp: {valid_ereignistypen_str}
- Beschreibung auf Deutsch mit gartenrelevanten Informationen (Standort, Pflege, Schnitt)
- Gib nur relevante Ereignisse an, die für diese Pflanze typisch sind"""


def _parse_autofill_response(raw: str) -> dict | None:
    """Parst die LLM-Antwort (JSON, ggf. aus Markdown-Codeblock)."""
    if raw is None:
        return None

    # Versuche zuerst, JSON aus einem Markdown-Codeblock zu extrahieren
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", raw, re.DOTALL)
    if match:
        json_str = match.group(1).strip()
        try:
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            pass

    # Versuche direkt als JSON zu parsen
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        pass

    return None


def _validate_autofill_data(data: dict) -> dict:
    """Validiert und bereinigt die geparsten Pflanzendaten."""
    result = {}

    # Einfache String-Felder
    result["beschreibung"] = data.get("beschreibung", "") if isinstance(data.get("beschreibung"), str) else ""
    result["typ"] = data.get("typ", "") if isinstance(data.get("typ"), str) else ""
    result["sorte"] = data.get("sorte", "") if isinstance(data.get("sorte"), str) else ""

    # Enum-Felder validieren
    lichtbedarf = data.get("lichtbedarf", "")
    result["lichtbedarf"] = lichtbedarf if lichtbedarf in VALID_LICHTBEDARF else ""

    lebensdauer = data.get("lebensdauer", "")
    result["lebensdauer"] = lebensdauer if lebensdauer in VALID_LEBENSDAUER else ""

    kategorie = data.get("kategorie", "")
    result["kategorie"] = kategorie if kategorie in VALID_KATEGORIEN else ""

    # Ereignisse validieren und filtern
    raw_ereignisse = data.get("ereignisse", [])
    if not isinstance(raw_ereignisse, list):
        raw_ereignisse = []

    valid_ereignisse = []
    for e in raw_ereignisse:
        if not isinstance(e, dict):
            continue

        ereignistyp = e.get("ereignistyp", "")
        if ereignistyp not in VALID_EREIGNISTYPEN:
            continue

        try:
            startmonat = int(e.get("startmonat", 0))
            endmonat = int(e.get("endmonat", 0))
        except (ValueError, TypeError):
            continue

        if not (1 <= startmonat <= 12) or not (1 <= endmonat <= 12):
            continue

        # Detail-Werte validieren
        start_detail = e.get("start_detail", "")
        if start_detail not in VALID_DETAIL:
            start_detail = ""

        end_detail = e.get("end_detail", "")
        if end_detail not in VALID_DETAIL:
            end_detail = ""

        valid_ereignisse.append({
            "ereignistyp": ereignistyp,
            "startmonat": startmonat,
            "endmonat": endmonat,
            "start_detail": start_detail,
            "end_detail": end_detail,
        })

    result["ereignisse"] = valid_ereignisse
    return result


@app.route("/api/autofill", methods=["POST"])
def api_autofill():
    """KI-Autofill: Gibt strukturierte Pflanzendaten als JSON zurück."""
    req_data = request.get_json()
    if not req_data or not req_data.get("name", "").strip():
        return jsonify({"ok": False, "error": "Bitte einen Pflanzennamen eingeben."}), 400

    if not is_llm_configured():
        return jsonify({"ok": False, "error": "KI-Dienst nicht konfiguriert. Bitte API-Key setzen."}), 500

    name = req_data["name"].strip()
    prompt = _build_autofill_prompt(name)

    try:
        provider = get_provider()
        raw = provider.generate(prompt)
    except Exception:
        return jsonify({"ok": False, "error": "KI-Dienst nicht erreichbar. Bitte später erneut versuchen."}), 502

    parsed = _parse_autofill_response(raw)
    if parsed is None:
        return jsonify({"ok": False, "error": "KI-Antwort konnte nicht verarbeitet werden."}), 502

    validated = _validate_autofill_data(parsed)
    return jsonify({"ok": True, "data": validated})
