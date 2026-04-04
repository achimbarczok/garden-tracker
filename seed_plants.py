"""Befüllungsskript: Pflanzen mit recherchierten Daten in die Datenbank eintragen.

Auf dem Raspberry Pi ausführen:
    docker exec garden-tracker python seed_plants.py

Oder lokal:
    DB_PATH=plants.db python seed_plants.py
"""
import os
import sys

# Damit db.py importiert werden kann
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, add_plant, add_ereignis, get_db

init_db()

# Prüfen ob schon Pflanzen vorhanden sind
existing = get_db().execute("SELECT COUNT(*) FROM plants").fetchone()[0]
if existing > 0:
    print(f"Datenbank enthält bereits {existing} Pflanzen. Skript wird abgebrochen.")
    print("Lösche die Datenbank oder entferne bestehende Einträge, bevor du das Skript erneut ausführst.")
    sys.exit(0)

# --- Pflanzendaten ---

plants_data = [
    {
        "name": "Herbsthimbeere",
        "kategorie": "Obst",
        "type": "Beerenobst",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": "Von Kikis Mutter, Sorte unbekannt. Ende Februar auf 5 cm über dem Boden schneiden.",
        "beschreibung": """Herbsthimbeere (Rubus idaeus)
Herbsthimbeeren tragen an den einjährigen Ruten und fruchten von August bis Oktober. Im Gegensatz zu Sommerhimbeeren werden alle Ruten im Spätwinter (Ende Februar) bodennah auf ca. 5 cm zurückgeschnitten. Standort: sonnig, humoser, leicht saurer Boden. Regelmäßig mulchen. Pflanzabstand ca. 40–50 cm in der Reihe.
Typische Sorten: Autumn Bliss, Polka, Heritage.""",
        "ereignisse": [
            ("Ernte", 8, 10),
            ("Rückschnitt", 2, 2),
        ],
    },
    {
        "name": "Brombeere",
        "kategorie": "Obst",
        "type": "Beerenobst",
        "variety": "Thornless Evergreen (vermutlich)",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": "Sorte vermutlich Thornless Evergreen. Am Drahtspalier leiten. Seitentriebe im September auf eine Handbreit (zwei Augen) einkürzen. Abgeerntete Ruten nach der Ernte oder im Spätwinter bodennah abschneiden.",
        "beschreibung": """Brombeere Thornless Evergreen (Rubus fruticosus)
Dornenlose, starkwüchsige Sorte mit hohem Ertrag. Früchte mittelgroß, süß-säuerlich, reifen ab August. Immergrün in milden Wintern. Benötigt ein Spalier oder Drahtsystem. Im Sommer die 3–6 kräftigsten neuen Ruten am Spalier hochleiten. Seitentriebe im September auf ca. 10 cm (zwei Augen) einkürzen. Abgeerntete Ruten nach der Ernte oder im Spätwinter bodennah entfernen. Standort: sonnig bis halbschattig, nährstoffreicher Boden.""",
        "ereignisse": [
            ("Blüte", 6, 7),
            ("Ernte", 8, 9),
            ("Rückschnitt", 9, 9),
        ],
    },
    {
        "name": "Apfel Boskoop",
        "kategorie": "Bäume",
        "type": "Kernobst",
        "variety": "Boskoop",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Apfel Boskoop (Malus domestica 'Schöner von Boskoop')
Alte, robuste Apfelsorte aus den Niederlanden (1856). Große, säuerliche Früchte, hervorragend zum Backen und Kochen. Triploid — braucht eine Befruchtersorte in der Nähe. Starker Wuchs, braucht regelmäßigen Erziehungsschnitt. Ernte Oktober, lagerfähig bis März. Anfällig für Schorf in feuchten Jahren. Standort: sonnig, tiefgründiger Boden.""",
        "ereignisse": [
            ("Blüte", 4, 5),
            ("Ernte", 10, 10),
            ("Rückschnitt", 1, 3),
        ],
    },
    {
        "name": "Forsythie",
        "kategorie": "Sträucher",
        "type": "Zierstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Forsythie (Forsythia × intermedia)
Frühblühender Zierstrauch, leuchtend gelbe Blüten vor dem Laubaustrieb. Wichtige Zeigerpflanze im phänologischen Kalender: Forsythienblüte markiert den Beginn des Erstfrühlings. Blüte März–April. Schnitt direkt nach der Blüte — älteste Triebe bodennah entfernen. Anspruchslos, verträgt fast jeden Boden. Keine Früchte für Insekten (gefüllte Blüten), daher ökologisch wenig wertvoll.""",
        "ereignisse": [
            ("Blüte", 3, 4),
            ("Rückschnitt", 4, 5),
        ],
    },
    {
        "name": "Lolla Bionda",
        "kategorie": "Gemüse",
        "type": "Pflücksalat",
        "variety": "Lolla Bionda",
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Lolla Bionda (Lactuca sativa var. crispa)
Hellgrüner, krausblättriger Pflücksalat mit mildem Geschmack. Schnellwachsend, erntereif nach ca. 6–8 Wochen. Kann als Pflücksalat laufend geerntet werden (äußere Blätter). Aussaat ab März (Vorkultur) oder April direkt ins Freiland, Folgesaaten bis August möglich. Verträgt Halbschatten gut. Schosst bei Hitze schnell — im Hochsommer schattigeren Standort wählen.""",
        "ereignisse": [
            ("Ernte", 5, 9),
        ],
    },
    {
        "name": "Eichblattsalat Bolchoi",
        "kategorie": "Gemüse",
        "type": "Pflücksalat",
        "variety": "Bolchoi",
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Eichblattsalat Bolchoi (Lactuca sativa var. crispa)
Rotbrauner Eichblattsalat mit zarten, gelappten Blättern. Milder, nussiger Geschmack. Schossfest und hitzeverträglich — gut für Sommeranbau. Aussaat ab März unter Glas, ab April direkt. Ernte nach ca. 8 Wochen. Als Pflücksalat über Wochen ernten. Verträgt Halbschatten.""",
        "ereignisse": [
            ("Ernte", 5, 9),
        ],
    },
    {
        "name": "Asiasalat Mizuna",
        "kategorie": "Gemüse",
        "type": "Blattgemüse",
        "variety": "Mizuna",
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Asiasalat Mizuna (Brassica rapa var. nipposinica)
Japanisches Blattgemüse mit fein gefiederten, milden Blättern. Schnellwachsend, erntereif nach 3–4 Wochen als Baby Leaf. Kann mehrfach geschnitten werden (Cut-and-come-again). Aussaat März–September, auch als Nachkultur geeignet. Kältetolerant, wächst noch im Herbst. Mild-würziger, leicht senfiger Geschmack.""",
        "ereignisse": [
            ("Ernte", 4, 10),
        ],
    },
    {
        "name": "Zuckererbse Buntblühende",
        "kategorie": "Gemüse",
        "type": "Hülsenfrucht",
        "variety": "Buntblühende",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Zuckererbse Buntblühende (Pisum sativum var. saccharatum)
Dekorative Zuckererbse mit rosa-violetten Blüten. Hülsen werden komplett gegessen (keine Fäden). Aussaat direkt ins Freiland ab März/April, sobald der Boden bearbeitbar ist. Rankhilfe nötig (ca. 100–150 cm hoch). Ernte ca. 10–12 Wochen nach Aussaat. Regelmäßig ernten fördert Nachblüte. Als Leguminose fixiert sie Stickstoff im Boden — gute Vorkultur.""",
        "ereignisse": [
            ("Blüte", 5, 7),
            ("Ernte", 6, 8),
        ],
    },
    {
        "name": "Radieschen Riesenbutter",
        "kategorie": "Gemüse",
        "type": "Wurzelgemüse",
        "variety": "Riesenbutter",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Radieschen Riesenbutter (Raphanus sativus var. sativus)
Große, runde Radieschensorte mit leuchtend roter Schale und weißem, mildem Fleisch. Wird deutlich größer als normale Radieschen ohne pelzig zu werden. Aussaat ab März direkt ins Freiland, Folgesaaten alle 2–3 Wochen bis September. Erntereif nach ca. 4–6 Wochen. Gleichmäßig feucht halten, sonst werden sie scharf und holzig.""",
        "ereignisse": [
            ("Ernte", 4, 10),
        ],
    },
    {
        "name": "Tomate Fredi",
        "kategorie": "Gemüse",
        "type": "Fruchtgemüse",
        "variety": "Fredi",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Tomate Fredi (Solanum lycopersicum)
Robuste Freilandtomate, samenfest. Rote, mittelgroße Früchte mit gutem Aroma. Widerstandsfähig gegen Kraut- und Braunfäule — gut für den Freilandanbau ohne Dach. Vorkultur ab März auf der Fensterbank, auspflanzen nach den Eisheiligen (Mitte Mai). Regelmäßig ausgeizen. Stütze/Stab nötig.""",
        "ereignisse": [
            ("Blüte", 6, 7),
            ("Ernte", 7, 9),
        ],
    },
    {
        "name": "Tomate Friesje",
        "kategorie": "Gemüse",
        "type": "Fruchtgemüse",
        "variety": "Friesje",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Tomate Friesje (Solanum lycopersicum)
Cocktailtomate mit rot-gelb gestreiften Früchten, süß-fruchtig im Geschmack. Ertragreich, lange Ernteperiode. Vorkultur ab März, auspflanzen nach den Eisheiligen. Regelmäßig ausgeizen und an Stab/Schnur leiten. Auch für Kübel geeignet.""",
        "ereignisse": [
            ("Blüte", 6, 7),
            ("Ernte", 7, 10),
        ],
    },
    {
        "name": "Ringelblume",
        "kategorie": "Blumen",
        "type": "Sommerblume",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Ringelblume (Calendula officinalis)
Robuste, anspruchslose Sommerblume mit leuchtend orangegelben Blüten. Blüht von Juni bis zum Frost. Heilpflanze (Wundheilung, Salben). Gute Mischkulturpartnerin — fördert Bodengesundheit, lockt Nützlinge an. Direktsaat ab April. Sät sich zuverlässig selbst aus.""",
        "ereignisse": [
            ("Blüte", 6, 10),
        ],
    },
    {
        "name": "Rucola",
        "kategorie": "Kräuter",
        "type": "Blattgemüse",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Rucola / Salatrauke (Eruca vesicaria)
Würziges Blattgemüse mit nussig-scharfem Geschmack. Schnellwachsend, erntereif nach 4–6 Wochen. Aussaat ab März bis September, Folgesaaten alle 3 Wochen. Schosst bei Hitze und Trockenheit schnell — im Sommer halbschattigen Standort wählen. Blüten sind essbar. Auch als Gründüngung nutzbar.""",
        "ereignisse": [
            ("Ernte", 4, 10),
        ],
    },
    {
        "name": "Phazelia",
        "kategorie": "Gründüngung",
        "type": "Bienenweide",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Phazelia / Bienenfreund (Phacelia tanacetifolia)
Hervorragende Gründüngung und Bienenweide. Lockert den Boden, unterdrückt Unkraut, bindet Nährstoffe. Nicht verwandt mit Gemüsefamilien — ideal als Zwischenfrucht ohne Fruchtfolgeprobleme. Aussaat April–September. Blüht nach ca. 6 Wochen, lavendelblaue Blüten. Friert im Winter ab und kann als Mulch liegen bleiben.""",
        "ereignisse": [
            ("Blüte", 6, 9),
        ],
    },
    {
        "name": "Stangenbohne Neckargold",
        "kategorie": "Gemüse",
        "type": "Hülsenfrucht",
        "variety": "Neckargold",
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": """Stangenbohne Neckargold (Phaseolus vulgaris)
Gelbe Wachsbohne, fadenlos, zart und buttrig im Geschmack. Ertragreich und robust. Aussaat ab Mitte Mai (frostempfindlich!) direkt an Stangen oder Rankgerüst. Klettert 2–3 m hoch. Ernte ab Juli bis zum Frost, regelmäßig pflücken fördert Nachblüte. Als Leguminose fixiert sie Stickstoff im Boden.""",
        "ereignisse": [
            ("Blüte", 6, 8),
            ("Ernte", 7, 10),
        ],
    },
]

# --- Einfügen ---

conn = get_db()
for p in plants_data:
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
print(f"\n{len(plants_data)} Pflanzen erfolgreich eingetragen.")
