"""Weitere Pflanzen hinzufügen: Hibiscus, Frühblüher, Stauden, Gehölze, Gemüse.

    DB_PATH=plants.db python seed_weitere_pflanzen.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, add_plant, add_ereignis, get_db

init_db()

plants_data = [
    {
        "name": "Hibiscus syriacus",
        "kategorie": "Gehölze",
        "type": "Zierstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Garteneibisch (Hibiscus syriacus) — sommergrüner Strauch, 2–3 m hoch, "
            "mit großen trichterförmigen Blüten von Juli bis September. Winterhart bis ca. −20 °C. "
            "Sonniger, geschützter Standort, durchlässiger, nährstoffreicher Boden. "
            "Rückschnitt im Frühjahr (März) auf 2–3 Augen der Vorjahrestriebe fördert reiche Blüte. "
            "Spätaustreiber — erst ab Mai belaubt.",
        "ereignisse": [
            ("Blüte", 7, 9),
            ("Rückschnitt", 3, 3),
        ],
    },
    {
        "name": "Osterglockennarzisse",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Osterglocke / Gelbe Narzisse (Narcissus pseudonarcissus) — "
            "klassischer Frühblüher mit gelben Trompetenblüten im März–April. "
            "Zwiebeln im Herbst (September–November) ca. 10–15 cm tief pflanzen. "
            "Sonniger bis halbschattiger Standort, humoser, durchlässiger Boden. "
            "Laub nach der Blüte einziehen lassen (nicht abschneiden). Verwildert gut.",
        "ereignisse": [
            ("Blüte", 3, 4),
        ],
    },
    {
        "name": "Traubenhyazinthe",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Traubenhyazinthe (Muscari) — kompakter Frühblüher mit traubenförmigen, "
            "meist blauen Blütenständen im März–April, 10–20 cm hoch. "
            "Zwiebeln im Herbst pflanzen, ca. 8 cm tief. Sonnig bis halbschattig, "
            "durchlässiger Boden. Sehr pflegeleicht, verwildert zuverlässig. "
            "Gute Begleitpflanze für Narzissen und Tulpen.",
        "ereignisse": [
            ("Blüte", 3, 4),
        ],
    },
    {
        "name": "Scilla",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Blaustern (Scilla siberica) — zierlicher Frühblüher mit intensiv blauen, "
            "nickenden Glöckchenblüten im März–April, 10–15 cm hoch. "
            "Zwiebeln im Herbst ca. 8 cm tief pflanzen. Halbschattig bis sonnig, "
            "humoser Boden. Extrem winterhart. Verwildert stark und bildet mit der Zeit "
            "dichte blaue Teppiche unter Gehölzen.",
        "ereignisse": [
            ("Blüte", 3, 4),
        ],
    },
    {
        "name": "Meerrettich",
        "kategorie": "Gemüse",
        "type": "Wurzelgemüse",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Meerrettich (Armoracia rusticana) — ausdauernde Staude mit kräftiger, "
            "scharfer Pfahlwurzel. Pflanzung im Frühjahr (März–April) als Fechser "
            "(Seitenwurzeln, schräg einsetzen). Sonniger Standort, tiefgründiger, "
            "humoser Boden. Ernte ab Oktober nach dem ersten Frost. "
            "Breitet sich stark aus — Wurzelsperre oder eigenes Beet empfehlenswert. "
            "Blätter können als Mulch verwendet werden.",
        "ereignisse": [
            ("Ernte", 10, 3),
            ("Auspflanzen", 3, 4),
        ],
    },
    {
        "name": "Anemone sylvestris",
        "kategorie": "Stauden",
        "type": "Wildstaude",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Waldanemone / Großes Windröschen (Anemone sylvestris) — "
            "heimische Wildstaude mit duftenden, schalenförmigen weißen Blüten (ca. 5 cm) "
            "im Mai–Juni, 20–30 cm hoch. Halbschattiger bis sonniger Standort, "
            "durchlässiger, kalkhaltiger Boden. Breitet sich über Ausläufer aus — "
            "guter Bodendecker. Bienenfreundlich. Weiße, wollige Samenstände im Sommer.",
        "ereignisse": [
            ("Blüte", 5, 6),
        ],
    },
    {
        "name": "Sommerflieder",
        "kategorie": "Gehölze",
        "type": "Zierstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Sommerflieder / Schmetterlingsstrauch (Buddleja davidii) — "
            "sommergrüner Strauch, 2–3 m hoch, mit langen, duftenden Blütenrispen "
            "von Juli bis Oktober in Violett, Rosa oder Weiß. Wichtige Nektarquelle "
            "für Schmetterlinge. Sonniger Standort, durchlässiger Boden. "
            "Kräftiger Rückschnitt im März auf 30–50 cm fördert kompakten Wuchs "
            "und reiche Blüte. Verblühtes regelmäßig entfernen verhindert Selbstaussaat.",
        "ereignisse": [
            ("Blüte", 7, 10),
            ("Rückschnitt", 3, 3),
        ],
    },
    {
        "name": "Schneeball",
        "kategorie": "Gehölze",
        "type": "Zierstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Gewöhnlicher Schneeball (Viburnum opulus) — heimischer, sommergrüner "
            "Strauch, 2–4 m hoch. Weiße, tellerförmige Blütenstände im Mai–Juni, "
            "leuchtend rote Beeren im Herbst, schöne Herbstfärbung. "
            "Sonnig bis halbschattig, feuchter, nährstoffreicher Boden. "
            "Schnitt direkt nach der Blüte. Ökologisch wertvoll — "
            "Vogelnahrung und Insektenweide.",
        "ereignisse": [
            ("Blüte", 5, 6),
            ("Rückschnitt", 6, 7),
        ],
    },
    {
        "name": "Rote Tulpen früh",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": "Frühe Sorte, rot blühend.",
        "beschreibung": "Frühe rote Tulpen (Tulipa) — Frühblüher mit leuchtend roten Blüten "
            "im März–April. Zwiebeln im Herbst (Oktober–November) ca. 10–15 cm tief pflanzen. "
            "Sonniger Standort, durchlässiger Boden. Laub nach der Blüte einziehen lassen. "
            "Frühe Sorten (Kaufmanniana, Fosteriana oder Single Early) blühen bereits ab März.",
        "ereignisse": [
            ("Blüte", 3, 4),
        ],
    },
]

plants_data += [
    {
        "name": "Rosa Tulpen früh",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": "Frühe Sorte, rosa blühend.",
        "beschreibung": "Frühe rosa Tulpen (Tulipa) — Frühblüher mit zarten rosa Blüten "
            "im März–April. Zwiebeln im Herbst (Oktober–November) ca. 10–15 cm tief pflanzen. "
            "Sonniger Standort, durchlässiger Boden. Laub nach der Blüte einziehen lassen. "
            "Frühe Sorten (Kaufmanniana, Fosteriana oder Single Early) blühen bereits ab März.",
        "ereignisse": [
            ("Blüte", 3, 4),
        ],
    },
    {
        "name": "Erdbeere",
        "kategorie": "Obst",
        "type": "Beerenobst",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": "Von Kikis Mutter, Sorte unbekannt.",
        "beschreibung": "Erdbeere (Fragaria × ananassa) — mehrjährige Staude mit süßen Früchten "
            "von Mai bis Juli (je nach Sorte). Sonniger Standort, humoser, leicht saurer Boden. "
            "Pflanzung im August oder Frühjahr. Stroh unterlegen gegen Fäulnis. "
            "Ausläufer zur Vermehrung nutzen oder entfernen für stärkere Mutterpflanze. "
            "Nach 3–4 Jahren Standort wechseln.",
        "ereignisse": [
            ("Blüte", 4, 5),
            ("Ernte", 5, 7),
        ],
    },
    {
        "name": "Feldsalat",
        "kategorie": "Gemüse",
        "type": "Blattgemüse",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Feldsalat / Rapunzel (Valerianella locusta) — winterharter Salat "
            "mit mildem, nussigem Geschmack. Aussaat Juli–September für Herbst-/Winterernte, "
            "oder Februar–März für Frühjahrsernte. Ernte ca. 8–10 Wochen nach Aussaat. "
            "Halbschattig bis sonnig, anspruchslos. Verträgt Frost bis −15 °C. "
            "Ideale Nachkultur nach Sommergemüse.",
        "ereignisse": [
            ("Ernte", 10, 3),
            ("Direktsaat", 7, 9),
        ],
    },
    {
        "name": "Rundblättrige Fetthenne",
        "kategorie": "Stauden",
        "type": "Sukkulente",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Rundblättrige Fetthenne (Hylotelephium ewersii, syn. Sedum ewersii) — "
            "niedrige, polsterbildende Sukkulente, 10–15 cm hoch, mit runden, "
            "blaugrünen, fleischigen Blättern. Rosa Blütendolden im August–September. "
            "Vollsonniger Standort, trockener, durchlässiger Boden (Steingarten, Mauerkronen). "
            "Extrem trockenheitsverträglich und winterhart. Bienenfreundlich. "
            "Zieht im Winter ein, treibt im Frühjahr neu aus.",
        "ereignisse": [
            ("Blüte", 8, 9),
        ],
    },
]

# --- Einfügen ---

conn = get_db()
for p in plants_data:
    # Prüfen ob schon vorhanden
    existing = conn.execute(
        "SELECT COUNT(*) FROM plants WHERE name = ?",
        (p["name"],),
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
         p.get("lebensdauer"), None, None,
         p.get("anzahl", 1), p["kategorie"], p.get("beschreibung")),
    )
    plant_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    for ereignistyp, start, end in p.get("ereignisse", []):
        conn.execute(
            "INSERT INTO ereignisse (plant_id, ereignistyp, startmonat, endmonat) "
            "VALUES (?, ?, ?, ?)",
            (plant_id, ereignistyp, start, end),
        )
    print(f"  ✓ {p['name']}")

conn.commit()
conn.close()
print(f"\n{len(plants_data)} Pflanzen verarbeitet.")
