# Implementierungsplan: Pflanzenereignisse

## Übersicht

Schrittweise Erweiterung des bestehenden Garden Trackers um Ereignisse, Lichtbedarf und Kommentar. Jeder Schritt baut auf dem vorherigen auf und endet mit vollständig verdrahteten Komponenten.

## Tasks

- [x] 1. Datenbankschicht erweitern (`db.py`)
  - [x] 1.1 Migration implementieren: `_migrate(conn)` und `init_db()` anpassen
    - `_migrate` prüft via `PRAGMA table_info(plants)`, ob `lichtbedarf` und `kommentar` fehlen, und führt `ALTER TABLE` durch
    - `CREATE TABLE IF NOT EXISTS ereignisse` mit `ON DELETE CASCADE`
    - `init_db()` ruft `_migrate` nach dem Anlegen der `plants`-Tabelle auf
    - _Anforderungen: 5.1, 5.2_
  - [x] 1.2 `add_plant()` um `lichtbedarf` und `kommentar` erweitern
    - Signatur: `add_plant(name, type, variety, lichtbedarf, kommentar)`
    - `kommentar = None` wenn leer
    - _Anforderungen: 3.1, 4.1_
  - [x] 1.3 `get_all_plants()` um neue Felder und Ereignisse erweitern
    - Spalten `lichtbedarf`, `kommentar` aus `plants` lesen
    - Für jede Pflanze alle zugehörigen Ereignisse aus `ereignisse` laden und als Liste `ereignisse` anhängen
    - _Anforderungen: 2.1, 3.4, 4.3, 5.3_
  - [x] 1.4 `add_ereignis()` und `remove_ereignis()` implementieren
    - `add_ereignis(plant_id, ereignistyp, startmonat, endmonat)` — INSERT in `ereignisse`
    - `remove_ereignis(ereignis_id)` — DELETE nach ID
    - _Anforderungen: 1.1, 1.2, 1.8_

- [x] 2. Validierung und neue Routen in `app.py`
  - [x] 2.1 `GERMAN_MONTHS`-Mapping und Validierungskonstanten definieren
    - `GERMAN_MONTHS = {1: "Januar", ..., 12: "Dezember"}`
    - `VALID_LICHTBEDARF = {"Sonne", "Halbschatten", "Schatten"}`
    - `VALID_EREIGNISTYPEN = {"Blüte", "Ernte", "Düngen", "Rückschnitt"}`
    - _Anforderungen: 1.3, 3.2_
  - [x] 2.2 `/add`-Route um Lichtbedarf-Validierung erweitern
    - `lichtbedarf` aus Formular lesen und gegen `VALID_LICHTBEDARF` prüfen
    - Bei ungültigem Wert: HTTP 400 + `"Lichtbedarf muss Sonne, Halbschatten oder Schatten sein."`
    - `add_plant()` mit neuen Parametern aufrufen
    - _Anforderungen: 3.1, 3.2, 3.3_
  - [x] 2.3 Route `POST /plant/<int:plant_id>/ereignis/add` implementieren
    - `ereignistyp`, `startmonat`, `endmonat` aus Formular lesen
    - Validierung: Typ in `VALID_EREIGNISTYPEN`, Monate 1–12, `startmonat <= endmonat`
    - Fehlermeldungen auf Deutsch, HTTP 400 bei Fehler
    - Bei Erfolg: `add_ereignis()` aufrufen, dann Redirect auf `/`
    - _Anforderungen: 1.2, 1.3, 1.4, 1.5_
  - [x] 2.4 Route `POST /ereignis/<int:ereignis_id>/remove` implementieren
    - `remove_ereignis(ereignis_id)` aufrufen, dann Redirect auf `/`
    - _Anforderungen: 1.8_
  - [x] 2.5 `GERMAN_MONTHS` als Template-Kontext-Variable übergeben
    - In der `index()`-Route `german_months=GERMAN_MONTHS` an `render_template` übergeben
    - _Anforderungen: 2.2_

- [x] 3. Checkpoint — Datenbankschicht und Routen
  - Sicherstellen, dass alle bisherigen Tests noch bestehen. Bei Fragen den Nutzer ansprechen.

- [x] 4. Template `index.html` erweitern
  - [x] 4.1 Pflanzentabelle um Spalten `Lichtbedarf` und `Kommentar` erweitern
    - Neue `<th>`-Einträge in der Tabellenkopfzeile
    - In jeder Zeile `plant.lichtbedarf` und `plant.kommentar` (leer wenn `None`) anzeigen
    - _Anforderungen: 3.4, 4.3, 4.4_
  - [x] 4.2 Ereignisliste pro Pflanze anzeigen
    - Innerhalb der Pflanzentabellenzeile alle `plant.ereignisse` auflisten
    - Jedes Ereignis zeigt: `ereignistyp`, `german_months[startmonat]`–`german_months[endmonat]`
    - Nur anzeigen wenn `plant.ereignisse` nicht leer ist
    - _Anforderungen: 2.1, 2.2, 2.3_
  - [x] 4.3 Formular zum Hinzufügen eines Ereignisses pro Pflanze
    - Pro Pflanze ein `<form method="post" action="/plant/{{ plant.id }}/ereignis/add">`
    - `<select name="ereignistyp">` mit den vier Optionen
    - `<select name="startmonat">` und `<select name="endmonat">` mit Werten 1–12 (deutsche Monatsnamen als Labels)
    - _Anforderungen: 1.1, 1.2, 1.3, 1.4_
  - [x] 4.4 Ereignis-Entfernen-Button pro Ereignis
    - Pro Ereignis ein `<form method="post" action="/ereignis/{{ ereignis.id }}/remove">` mit Entfernen-Button
    - _Anforderungen: 1.8_
  - [x] 4.5 Hinzufügen-Formular um `lichtbedarf` und `kommentar` erweitern
    - `<select name="lichtbedarf">` mit Optionen Sonne, Halbschatten, Schatten (Pflichtfeld)
    - `<textarea name="kommentar">` (optional)
    - _Anforderungen: 3.1, 4.1_

- [x] 5. Finaler Checkpoint — Alle Tests bestehen
  - Sicherstellen, dass alle Tests (bestehende und neue) bestehen. Bei Fragen den Nutzer ansprechen.

## Hinweise

- Jeder Task referenziert spezifische Anforderungen zur Rückverfolgbarkeit
- Alle Fehlermeldungen müssen auf Deutsch sein
