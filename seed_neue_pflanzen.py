"""Ergänzungsskript: Weitere Pflanzen in die bestehende Datenbank eintragen.

Auf dem Raspberry Pi ausführen:
    docker exec garden-tracker python seed_neue_pflanzen.py

Oder lokal:
    DB_PATH=plants.db python seed_neue_pflanzen.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, add_plant, add_ereignis, get_db

init_db()

plants_data = [
    {
        "name": "Erdbeere Korona",
        "kategorie": "Obst",
        "type": "Beerenobst",
        "variety": "Korona",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 10,
        "pflanzmonat": 3,
        "pflanzjahr": 2026,
        "kommentar": "10 Pflanzen, gepflanzt Ende März 2026.",
        "beschreibung": """Erdbeere Korona (Fragaria × ananassa 'Korona')
Beliebte mittelfrühe Erdbeersorte (Juniträger) mit großen, dunkelroten Früchten und intensivem, süß-aromatischem Geschmack. Erntezeitraum ca. 3–4 Wochen im Juni. Hoher Ertrag, robuste Pflanze. Standort: sonnig, humoser, gut durchlässiger Boden. Pflanzabstand ca. 30 cm. Nach der Ernte altes Laub entfernen. Im Frühjahr und nach der Ernte düngen. Ausläufer regelmäßig entfernen, sofern keine Vermehrung gewünscht. Empfindlich gegen Grauschimmel bei Nässe — Stroh unterlegen.""",
        "ereignisse": [
            ("Blüte", 5, 5, "Anfang", "Ende"),
            ("Ernte", 6, 6, "Anfang", "Ende"),
            ("Düngen", 3, 3, None, None),
            ("Düngen", 7, 7, None, None),
        ],
    },
    {
        "name": "Rote Johannisbeere",
        "kategorie": "Obst",
        "type": "Beerenobst",
        "variety": "Jonkheer van Tets",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "pflanzmonat": 6,
        "pflanzjahr": 2017,
        "kommentar": "Eingepflanzt vermutlich Juni 2017.",
        "beschreibung": """Rote Johannisbeere Jonkheer van Tets (Ribes rubrum 'Jonkheer van Tets')
Frühe, ertragreiche Sorte roter Johannisbeeren aus den Niederlanden. Aufrechter Wuchs, große süße Früchte an langen Trauben. Eine der frühesten Sorten — Ernte bereits ab Ende Juni. Blüte im April. Selbstfruchtbar, aber Ertrag steigt mit Befruchtersorte. Standort: sonnig bis halbschattig, nährstoffreicher Boden. Auslichtungsschnitt im Winter: älteste Triebe (4+ Jahre) bodennah entfernen, 8–10 kräftige Triebe stehen lassen.""",
        "ereignisse": [
            ("Blüte", 4, 4, None, None),
            ("Ernte", 6, 7, "Ende", "Mitte"),
            ("Rückschnitt", 1, 2, None, None),
        ],
    },
    {
        "name": "Brautspiere",
        "kategorie": "Sträucher",
        "type": "Zierstrauch",
        "variety": "Spiraea arguta",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "pflanzmonat": 4,
        "pflanzjahr": 2018,
        "kommentar": "Gepflanzt April 2018.",
        "beschreibung": """Brautspiere (Spiraea arguta)
Frühjahrsblühender Zierstrauch mit überhängenden Trieben, die im April dicht mit kleinen weißen Blüten besetzt sind. Wird 1,5–2 m hoch und breit. Anspruchslos, verträgt fast jeden Boden. Schnitt direkt nach der Blüte — älteste Triebe bodennah entfernen, da die Blüten am vorjährigen Holz erscheinen. Herbstfärbung gelb-orange. Guter Sichtschutz und Bienenweide im Frühling.""",
        "ereignisse": [
            ("Blüte", 4, 4, "Mitte", "Ende"),
            ("Rückschnitt", 5, 5, "Anfang", "Mitte"),
        ],
    },
    {
        "name": "Stachelbeere",
        "kategorie": "Obst",
        "type": "Beerenobst",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "pflanzmonat": None,
        "pflanzjahr": 2016,
        "kommentar": "Sorte unbekannt, war bereits im Schrebergarten vorhanden (seit Herbst 2016).",
        "beschreibung": """Stachelbeere (Ribes uva-crispa)
Robuster Beerenstrauch, der sowohl in Sonne als auch Halbschatten gedeiht. Blüte März bis Mai, Ernte Juni bis Juli. Früchte je nach Sorte grün, gelb oder rot. Auslichtungsschnitt im Winter: älteste Triebe (4+ Jahre) entfernen, Strauch auf 8–10 Triebe begrenzen. Anfällig für Mehltau — luftigen Standort wählen und nicht zu dicht pflanzen. Verträgt Halbschatten besser als die meisten Beerenobstarten.""",
        "ereignisse": [
            ("Blüte", 3, 5, None, None),
            ("Ernte", 6, 7, None, None),
            ("Rückschnitt", 1, 2, None, None),
        ],
    },
]

# --- Einfügen ---

conn = get_db()
count = 0
for p in plants_data:
    # Prüfen ob Pflanze mit gleichem Namen schon existiert
    existing = conn.execute(
        "SELECT COUNT(*) FROM plants WHERE name = ?", (p["name"],)
    ).fetchone()[0]
    if existing > 0:
        print(f"  ⏭ {p['name']} existiert bereits, übersprungen.")
        continue

    conn.execute(
        "INSERT INTO plants (name, type, variety, lichtbedarf, kommentar, "
        "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, beschreibung) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (p["name"], p.get("type", ""), p.get("variety"),
         p["lichtbedarf"], p.get("kommentar"),
         p.get("lebensdauer"), p.get("pflanzmonat"),
         p.get("pflanzjahr"), p.get("anzahl", 1),
         p["kategorie"], p.get("beschreibung")),
    )
    plant_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    for ereignis in p.get("ereignisse", []):
        ereignistyp, start, end = ereignis[0], ereignis[1], ereignis[2]
        start_detail = ereignis[3] if len(ereignis) > 3 else None
        end_detail = ereignis[4] if len(ereignis) > 4 else None
        conn.execute(
            "INSERT INTO ereignisse (plant_id, ereignistyp, startmonat, endmonat, "
            "start_detail, end_detail) VALUES (?, ?, ?, ?, ?, ?)",
            (plant_id, ereignistyp, start, end, start_detail, end_detail),
        )
    print(f"  ✓ {p['name']}")
    count += 1

conn.commit()
conn.close()

if count > 0:
    print(f"\n{count} Pflanze(n) erfolgreich eingetragen.")
else:
    print("\nKeine neuen Pflanzen eingetragen (alle bereits vorhanden).")
