"""Neue Gartenpflege-Einträge hinzufügen: Kompost und Gartenlaube.

    DB_PATH=plants.db python seed_neue_pflanzen.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, add_plant, get_db

init_db()

neue_eintraege = [
    {
        "name": "Kompost",
        "kategorie": "Gartenpflege",
        "type": "",
        "variety": None,
        "lichtbedarf": "Schatten",
        "lebensdauer": None,
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Komposthaufen — regelmäßig umschichten, feucht halten, Material schichten.",
    },
    {
        "name": "Gartenlaube",
        "kategorie": "Gartenpflege",
        "type": "",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": None,
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Gartenlaube — Holzpflege, Dach prüfen, Reinigung.",
    },
]

conn = get_db()
for p in neue_eintraege:
    # Prüfen ob schon vorhanden
    existing = conn.execute(
        "SELECT COUNT(*) FROM plants WHERE name = ? AND kategorie = ?",
        (p["name"], p["kategorie"]),
    ).fetchone()[0]
    if existing > 0:
        print(f"  ⏭ {p['name']} existiert bereits, übersprungen.")
        continue
    conn.execute(
        "INSERT INTO plants (name, type, variety, lichtbedarf, kommentar, "
        "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, beschreibung) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (p["name"], p["type"], p["variety"], p["lichtbedarf"], p["kommentar"],
         p["lebensdauer"], None, None, p["anzahl"], p["kategorie"], p["beschreibung"]),
    )
    print(f"  ✓ {p['name']}")

conn.commit()
conn.close()
print(f"\nFertig.")
