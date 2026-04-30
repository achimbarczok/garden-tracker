"""Weitere Pflanzen hinzufügen: Wildtulpe, Lavendel, Salbei, Fetthenne, Kamille,
Pfingstrose, Feige, Deutsche Schwertlilie, Thymian, Prärie-Lilie, Hasenglöckchen,
Rosmarin-Seidelbast, Weintraube, Gemeiner Efeu, Kartoffel-Rose, Katzenminze,
Rosmarin, Vergissmeinnicht, sowie Meisen-Häuschen als Gartenpflege-Eintrag.

    DB_PATH=plants.db python seed_wildtulpe_etc.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import init_db, get_db

init_db()

plants_data = [
    {
        "name": "Wildtulpe",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Wildtulpe (Tulipa sylvestris) — zierliche, heimische Tulpenart mit "
            "leuchtend gelben, nickenden Blüten im April–Mai, 20–30 cm hoch. "
            "Zwiebeln im Herbst ca. 10 cm tief pflanzen. Sonniger bis halbschattiger Standort, "
            "durchlässiger Boden. Verwildert zuverlässig über Ausläufer und bildet mit der Zeit "
            "dichte Bestände. Geschützte Art — nur aus Kultur beziehen. Duftend.",
        "ereignisse": [
            ("Blüte", 4, 5),
        ],
    },
    {
        "name": "Lavendel",
        "kategorie": "Stauden",
        "type": "Halbstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Echter Lavendel (Lavandula angustifolia) — immergrüner Halbstrauch, "
            "30–60 cm hoch, mit aromatischen, silbergrauen Blättern und violetten Blütenähren "
            "von Juni bis August. Vollsonniger Standort, magerer, durchlässiger, kalkhaltiger Boden. "
            "Rückschnitt nach der Blüte (August) um ein Drittel, zweiter leichter Schnitt im Frühjahr "
            "(März) ins alte Holz vermeiden. Bienenweide. Duftet intensiv, hält Blattläuse fern. "
            "Winterhart bis ca. −15 °C.",
        "ereignisse": [
            ("Blüte", 6, 8),
            ("Rückschnitt", 8, 8),
            ("Rückschnitt", 3, 3),
        ],
    },
    {
        "name": "Salbei",
        "kategorie": "Kräuter",
        "type": "Halbstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Echter Salbei (Salvia officinalis) — immergrüner Halbstrauch, "
            "40–60 cm hoch, mit samtigen, graugrünen Blättern und blauvioletten Lippenblüten "
            "im Juni–Juli. Vollsonniger Standort, durchlässiger, kalkhaltiger Boden. "
            "Rückschnitt im Frühjahr (März–April) auf ca. 15 cm fördert buschigen Wuchs. "
            "Nicht ins alte Holz schneiden. Küchenkraut (Tee, Fleisch, Pasta), Heilpflanze. "
            "Bienenfreundlich. Winterhart bis ca. −15 °C.",
        "ereignisse": [
            ("Blüte", 6, 7),
            ("Ernte", 5, 10),
            ("Rückschnitt", 3, 4),
        ],
    },
    {
        "name": "Fetthenne",
        "kategorie": "Stauden",
        "type": "Sukkulente",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Hohe Fetthenne (Hylotelephium spectabile, syn. Sedum spectabile) — "
            "aufrechte Staude, 40–60 cm hoch, mit fleischigen, blaugrünen Blättern und großen, "
            "flachen Blütendolden in Rosa bis Karminrot von August bis Oktober. "
            "Vollsonniger Standort, durchlässiger, eher magerer Boden. Extrem trockenheitsverträglich. "
            "Wichtige Spätblüher-Nahrungsquelle für Bienen und Schmetterlinge. "
            "Vertrocknete Stängel als Winterschmuck stehen lassen, Rückschnitt im Frühjahr.",
        "ereignisse": [
            ("Blüte", 8, 10),
            ("Rückschnitt", 3, 3),
        ],
    },
    {
        "name": "Kamille",
        "kategorie": "Kräuter",
        "type": "Heilkraut",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Einjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Echte Kamille (Matricaria chamomilla) — einjährige Heilpflanze, "
            "20–50 cm hoch, mit fein gefiederten Blättern und weißen Korbblüten mit gelbem Zentrum "
            "von Mai bis August. Sonniger Standort, magerer, durchlässiger Boden. "
            "Direktsaat ab März, Lichtkeimer (nicht bedecken). Blütenköpfe bei trockenem Wetter ernten "
            "und trocknen für Tee. Sät sich zuverlässig selbst aus. "
            "Gute Mischkulturpartnerin, fördert Bodengesundheit.",
        "ereignisse": [
            ("Blüte", 5, 8),
            ("Ernte", 5, 8),
            ("Direktsaat", 3, 4),
        ],
    },
    {
        "name": "Pfingstrose",
        "kategorie": "Stauden",
        "type": "Blütenstaude",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Pfingstrose (Paeonia lactiflora) — langlebige Staude, 60–100 cm hoch, "
            "mit großen, duftenden, gefüllten oder einfachen Blüten in Weiß, Rosa oder Rot "
            "im Mai–Juni. Sonniger Standort, tiefgründiger, nährstoffreicher, lehmiger Boden. "
            "Pflanzung im Herbst (September–Oktober), Augen max. 3–5 cm unter der Erde — "
            "zu tiefes Pflanzen verhindert Blüte. Nicht umpflanzen, wird mit den Jahren schöner. "
            "Stütze für schwere Blüten empfehlenswert. Kann 50+ Jahre am selben Standort stehen.",
        "ereignisse": [
            ("Blüte", 5, 6),
        ],
    },
    {
        "name": "Feige",
        "kategorie": "Gehölze",
        "type": "Obstgehölz",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Echte Feige (Ficus carica) — sommergrüner Großstrauch oder kleiner Baum, "
            "2–5 m hoch, mit großen, gelappten Blättern. Zwei Ernten möglich: Vorfeigen (Juni–Juli) "
            "an Vorjahrestrieben, Haupternte (August–Oktober) an diesjährigen Trieben. "
            "Geschützter, vollsonniger, warmer Standort (Südwand ideal). Durchlässiger, "
            "nährstoffreicher Boden. Winterschutz in rauen Lagen (Vlies, Mulch). "
            "Winterhart bis ca. −12 bis −15 °C je nach Sorte. Leichter Auslichtungsschnitt im Frühjahr.",
        "ereignisse": [
            ("Ernte", 6, 7, "Mitte", "Ende"),
            ("Ernte", 8, 10),
            ("Rückschnitt", 3, 4),
        ],
    },
    {
        "name": "Deutsche Schwertlilie",
        "kategorie": "Stauden",
        "type": "Blütenstaude",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Deutsche Schwertlilie / Bartiris (Iris germanica) — "
            "stattliche Staude, 60–100 cm hoch, mit schwertförmigen, graugrünen Blättern "
            "und großen, eleganten Blüten in Blau, Violett, Weiß oder Gelb im Mai–Juni. "
            "Vollsonniger Standort, durchlässiger, kalkhaltiger Boden. Rhizome flach pflanzen — "
            "Oberseite muss sichtbar bleiben (Sonnenanbeter). Pflanzzeit Juli–September. "
            "Alle 3–4 Jahre teilen, um Blühfreudigkeit zu erhalten. Trockenheitsverträglich.",
        "ereignisse": [
            ("Blüte", 5, 6),
        ],
    },
    {
        "name": "Thymian",
        "kategorie": "Kräuter",
        "type": "Halbstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Echter Thymian (Thymus vulgaris) — immergrüner, aromatischer Halbstrauch, "
            "15–30 cm hoch, mit kleinen, graugrünen Blättern und rosa-violetten Lippenblüten "
            "im Juni–Juli. Vollsonniger Standort, magerer, durchlässiger, kalkhaltiger Boden. "
            "Rückschnitt im Frühjahr (März–April) auf ca. 10 cm, nicht ins alte Holz schneiden. "
            "Küchenkraut (mediterrane Küche), Heilpflanze (Hustentee). "
            "Bienenweide. Winterhart bis ca. −15 °C.",
        "ereignisse": [
            ("Blüte", 6, 7),
            ("Ernte", 5, 10),
            ("Rückschnitt", 3, 4),
        ],
    },
    {
        "name": "Prärie-Lilie",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Prärie-Lilie / Prärielilie (Camassia) — elegante Zwiebelpflanze, "
            "60–80 cm hoch, mit sternförmigen, blauen bis violetten Blüten in langen Trauben "
            "im Mai–Juni. Zwiebeln im Herbst ca. 10–15 cm tief pflanzen. "
            "Sonniger bis halbschattiger Standort, frischer bis feuchter, nährstoffreicher Boden. "
            "Verträgt auch schwere Böden und zeitweise Staunässe. Verwildert gut. "
            "Bienenfreundlich. Laub nach der Blüte einziehen lassen.",
        "ereignisse": [
            ("Blüte", 5, 6),
        ],
    },
    {
        "name": "Hasenglöckchen",
        "kategorie": "Blumen",
        "type": "Zwiebelpflanze",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Hasenglöckchen (Hyacinthoides non-scripta) — zierliche Zwiebelpflanze, "
            "20–40 cm hoch, mit nickenden, glockenförmigen, blauen Blüten in einseitswendigen "
            "Trauben im April–Mai. Halbschattiger bis schattiger Standort, humoser, "
            "frischer Boden. Ideal unter Laubgehölzen. Zwiebeln im Herbst ca. 8–10 cm tief pflanzen. "
            "Verwildert zuverlässig und bildet mit der Zeit dichte Blütenteppiche. "
            "Duftend. Alle Pflanzenteile giftig.",
        "ereignisse": [
            ("Blüte", 4, 5),
        ],
    },
    {
        "name": "Rosmarin-Seidelbast",
        "kategorie": "Gehölze",
        "type": "Zierstrauch",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Rosmarin-Seidelbast (Daphne cneorum) — immergrüner, niederliegender "
            "Zwergstrauch, 15–30 cm hoch, mit schmalen, rosmarin-ähnlichen Blättern und "
            "intensiv duftenden, rosa Blüten im April–Mai. Halbschattiger bis sonniger Standort, "
            "durchlässiger, kalkhaltiger, humoser Boden. Nicht umpflanzen — empfindliche Wurzeln. "
            "Kein Rückschnitt nötig. Winterhart. Alle Pflanzenteile stark giftig. "
            "Geschützte heimische Art — nur aus Kultur beziehen.",
        "ereignisse": [
            ("Blüte", 4, 5),
        ],
    },
    {
        "name": "Weintraube",
        "kategorie": "Obst",
        "type": "Kletterpflanze",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Weinrebe (Vitis vinifera) — kletternder Strauch, der mit Ranken "
            "an Spalieren, Pergolen oder Hauswänden bis 10 m hoch wächst. "
            "Vollsonniger, warmer, geschützter Standort (Südseite ideal). "
            "Tiefgründiger, durchlässiger, kalkhaltiger Boden. "
            "Winterschnitt (Januar–Februar) auf 2 Augen am Zapfen. "
            "Sommerschnitt: Geiztriebe entfernen, Traubenzone entblättern. "
            "Ernte September–Oktober je nach Sorte. Winterhart bis ca. −15 bis −20 °C.",
        "ereignisse": [
            ("Blüte", 6, 6),
            ("Ernte", 9, 10),
            ("Rückschnitt", 1, 2),
        ],
    },
    {
        "name": "Gemeiner Efeu",
        "kategorie": "Gehölze",
        "type": "Kletterpflanze",
        "variety": None,
        "lichtbedarf": "Schatten",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Gemeiner Efeu (Hedera helix) — immergrüner, selbstklimmender Kletterstrauch, "
            "der mit Haftwurzeln an Mauern, Bäumen und Zäunen bis 20 m hoch klettert. "
            "Auch als Bodendecker verwendbar. Schattig bis halbschattig, anspruchslos an den Boden. "
            "Blüte erst an Altersform (September–Oktober) — wichtige Spätnahrung für Bienen. "
            "Schwarze Beeren im Winter — Vogelnahrung. Rückschnitt jederzeit möglich. "
            "Alle Pflanzenteile giftig. Extrem winterhart.",
        "ereignisse": [
            ("Blüte", 9, 10),
        ],
    },
    {
        "name": "Kartoffel-Rose",
        "kategorie": "Gehölze",
        "type": "Wildrose",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Kartoffel-Rose / Apfelrose (Rosa rugosa) — robuster, dicht verzweigter "
            "Wildrosenstrauch, 1–2 m hoch, mit stark bestachelten Trieben und runzeligen Blättern. "
            "Große, duftende, einfache Blüten in Rosa oder Weiß von Juni bis September (Dauerblüher). "
            "Große, fleischige Hagebutten ab August — essbar, reich an Vitamin C. "
            "Sonniger Standort, sandiger bis lehmiger Boden, salztolerant. "
            "Extrem winterhart und anspruchslos. Bildet Ausläufer — Wurzelsperre empfehlenswert.",
        "ereignisse": [
            ("Blüte", 6, 9),
            ("Ernte", 8, 10),
        ],
    },
    {
        "name": "Katzenminze",
        "kategorie": "Stauden",
        "type": "Blütenstaude",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Katzenminze (Nepeta × faassenii) — buschige Staude, 30–50 cm hoch, "
            "mit aromatischen, graugrünen Blättern und lavendelblauen Blütenähren "
            "von Mai bis September. Vollsonniger Standort, durchlässiger, eher magerer Boden. "
            "Nach der ersten Blüte (Juli) bodennah zurückschneiden — blüht dann ein zweites Mal. "
            "Hervorragende Bienenweide und Begleitpflanze für Rosen. "
            "Trockenheitsverträglich. Winterhart.",
        "ereignisse": [
            ("Blüte", 5, 9),
            ("Rückschnitt", 7, 7),
        ],
    },
    {
        "name": "Rosmarin",
        "kategorie": "Kräuter",
        "type": "Halbstrauch",
        "variety": None,
        "lichtbedarf": "Sonne",
        "lebensdauer": "Mehrjährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Rosmarin (Salvia rosmarinus, syn. Rosmarinus officinalis) — "
            "immergrüner, aromatischer Halbstrauch, 50–150 cm hoch, mit nadelförmigen, "
            "dunkelgrünen Blättern und hellblauen Lippenblüten im März–Mai. "
            "Vollsonniger, warmer, geschützter Standort (Südwand). Durchlässiger, "
            "kalkhaltiger, magerer Boden. Staunässe vermeiden. "
            "Leichter Formschnitt nach der Blüte, nicht ins alte Holz schneiden. "
            "Küchenkraut (mediterrane Küche). Winterhart bis ca. −10 °C — "
            "in rauen Lagen Winterschutz oder Kübelhaltung.",
        "ereignisse": [
            ("Blüte", 3, 5),
            ("Ernte", 3, 11),
            ("Rückschnitt", 5, 6),
        ],
    },
    {
        "name": "Vergissmeinnicht",
        "kategorie": "Blumen",
        "type": "Sommerblume",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": "Zweijährig",
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Vergissmeinnicht (Myosotis sylvatica) — zweijährige Pflanze, "
            "15–30 cm hoch, mit kleinen, himmelblauen Blüten mit gelbem Auge "
            "im April–Juni. Halbschattiger bis sonniger Standort, frischer, humoser Boden. "
            "Aussaat Juni–Juli, blüht im Folgejahr. Sät sich zuverlässig selbst aus "
            "und verwildert leicht. Klassische Frühlingsblume, guter Begleiter für Tulpen "
            "und Narzissen. Bienenfreundlich.",
        "ereignisse": [
            ("Blüte", 4, 6),
        ],
    },
    {
        "name": "Meisen-Häuschen",
        "kategorie": "Gartenpflege",
        "type": "",
        "variety": None,
        "lichtbedarf": "Halbschatten",
        "lebensdauer": None,
        "anzahl": 1,
        "kommentar": None,
        "beschreibung": "Nistkasten für Meisen (Kohlmeise, Blaumeise). "
            "Einflugloch 26–28 mm (Blaumeise) oder 32 mm (Kohlmeise). "
            "Aufhängen in 2–3 m Höhe, Einflugloch nach Osten oder Südosten. "
            "Jährliche Reinigung im September/Oktober nach der Brutsaison — "
            "altes Nest entfernen, mit heißem Wasser ausspülen. "
            "Nicht zu nah an Futterstellen aufhängen.",
        "ereignisse": [
            ("Pflege", 9, 10),
        ],
    },
]

# --- Einfügen ---

conn = get_db()
inserted = 0
skipped = 0

for p in plants_data:
    # Prüfen ob schon vorhanden
    existing = conn.execute(
        "SELECT COUNT(*) FROM plants WHERE name = ?",
        (p["name"],),
    ).fetchone()[0]
    if existing > 0:
        print(f"  ⏭ {p['name']} existiert bereits, übersprungen.")
        skipped += 1
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

    for ereignis in p.get("ereignisse", []):
        ereignistyp = ereignis[0]
        startmonat = ereignis[1]
        endmonat = ereignis[2]
        start_detail = ereignis[3] if len(ereignis) > 3 else None
        end_detail = ereignis[4] if len(ereignis) > 4 else None
        conn.execute(
            "INSERT INTO ereignisse (plant_id, ereignistyp, startmonat, endmonat, "
            "start_detail, end_detail) VALUES (?, ?, ?, ?, ?, ?)",
            (plant_id, ereignistyp, startmonat, endmonat, start_detail, end_detail),
        )

    print(f"  ✓ {p['name']}")
    inserted += 1

conn.commit()
conn.close()
print(f"\n{inserted} Pflanzen eingefügt, {skipped} übersprungen.")
