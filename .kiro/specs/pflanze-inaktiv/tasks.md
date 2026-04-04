# Implementation Plan: Pflanze inaktiv setzen

## Übersicht

Erweitert den Garten-Tracker um die Möglichkeit, Pflanzen als „inaktiv" zu markieren statt sie zu löschen. Umfasst DB-Migration, neue DB-Funktion, zwei neue POST-Routen, Filterlogik in der Pflanzenliste, visuelle Kennzeichnung inaktiver Pflanzen und kontextabhängige Buttons auf der Bearbeitungsseite.

## Tasks

- [x] 1. Datenbank-Migration und neue DB-Funktion `set_plant_active`
  - [x] 1.1 Migration: `aktiv`-Spalte in `_migrate()` hinzufügen
    - In `db.py` `_migrate()`: Prüfe via `PRAGMA table_info(plants)` ob `aktiv` existiert
    - Falls nicht: `ALTER TABLE plants ADD COLUMN aktiv INTEGER DEFAULT 1`
    - _Requirements: 1.1, 1.2, 1.4_

  - [x] 1.2 Neue Funktion `set_plant_active(plant_id, aktiv)` in `db.py`
    - `UPDATE plants SET aktiv = ? WHERE id = ?`
    - Eigene Verbindung via `get_db()`, öffnen/schließen
    - _Requirements: 2.2, 3.2_

  - [x] 1.3 `get_all_plants()` um Parameter `include_inactive` erweitern
    - Neuer optionaler Parameter `include_inactive: bool = False`
    - `include_inactive=False`: `WHERE aktiv = 1`
    - `include_inactive=True`: kein Filter auf `aktiv`
    - Feld `aktiv` in SELECT aufnehmen
    - _Requirements: 4.1, 4.3_

  - [x] 1.4 `get_plant()` um Feld `aktiv` in SELECT erweitern
    - Kein Filter auf `aktiv` — inaktive Pflanzen bleiben über Direktlink erreichbar
    - _Requirements: 6.1_

  - [x] 1.5 `duplicate_plant()` anpassen: Duplikat immer mit `aktiv = 1`
    - In der INSERT-Anweisung `aktiv = 1` explizit setzen
    - _Requirements: 7.1_

- [x] 2. Checkpoint — DB-Schicht prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Neue Routen in `app.py`
  - [x] 3.1 Import `set_plant_active` aus `db.py` hinzufügen
    - _Requirements: 2.2, 3.2_

  - [x] 3.2 Route `POST /plant/<int:plant_id>/deactivate` implementieren
    - `get_plant(plant_id)` → `abort(404)` wenn `None`
    - `set_plant_active(plant_id, 0)` in try/except
    - Bei DB-Fehler: Redirect auf `/` ohne Statusänderung
    - Bei Erfolg: Redirect auf `/` (HTTP 302)
    - _Requirements: 2.2, 2.4, 8.1, 8.2_

  - [x] 3.3 Route `POST /plant/<int:plant_id>/activate` implementieren
    - `get_plant(plant_id)` → `abort(404)` wenn `None`
    - `set_plant_active(plant_id, 1)` in try/except
    - Bei DB-Fehler: Redirect auf `/` ohne Statusänderung
    - Bei Erfolg: Redirect auf `/plant/<id>/edit` (HTTP 302)
    - _Requirements: 3.2, 3.3, 8.1, 8.2_

  - [x] 3.4 `index()`-Route anpassen: `show_inactive` Query-Parameter auswerten
    - `request.args.get("show_inactive", "")` auslesen
    - `get_all_plants(include_inactive=bool(show_inactive))` aufrufen
    - `show_inactive`-Flag an Template übergeben
    - _Requirements: 4.1, 4.3_

- [x] 4. Template-Änderungen: `index.html`
  - [x] 4.1 Filter-Schalter „Inaktive anzeigen" im Filter-Bereich hinzufügen
    - Checkbox mit `onchange="this.form.submit()"` im bestehenden Filter-Formular
    - Bestehende Filter-Parameter als hidden fields beibehalten
    - _Requirements: 4.2, 4.3_

  - [x] 4.2 Visuelle Kennzeichnung inaktiver Pflanzen in der Tabelle
    - CSS-Klasse `row-inactive` auf `<tr>` wenn `plant.aktiv == 0`
    - Badge `<span class="badge badge-inactive">inaktiv</span>` neben dem Pflanzennamen
    - _Requirements: 4.4_

- [x] 5. Template-Änderungen: `edit.html`
  - [x] 5.1 Hinweisbanner für inaktive Pflanzen
    - `{% if not plant.aktiv %}` → `<div class="alert-inactive">💤 Diese Pflanze ist inaktiv.</div>`
    - Platzierung nach der Überschrift, vor dem Formular
    - _Requirements: 5.1_

  - [x] 5.2 Kontextabhängiger Button (Inaktiv setzen / Aktivieren)
    - Neuer Abschnitt zwischen „Duplizieren" und „Pflanze entfernen"
    - Aktive Pflanze: Button „Inaktiv setzen" → POST `/plant/<id>/deactivate`
    - Inaktive Pflanze: Button „Aktivieren" → POST `/plant/<id>/activate`
    - _Requirements: 2.1, 3.1, 5.2_

- [x] 6. CSS-Änderungen in `static/style.css`
  - Klasse `.row-inactive` mit `opacity: 0.5` und hover `opacity: 0.7`
  - Klasse `.badge-inactive` für das Inaktiv-Badge
  - Klasse `.alert-inactive` für das Hinweisbanner auf der Bearbeitungsseite
  - _Requirements: 4.4, 5.1_

- [x] 7. Checkpoint — Manuelle Prüfung der UI
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Property-Based Tests (Hypothesis)
  - [x] 8.1 Property 1: Neue Pflanzen sind standardmäßig aktiv
    - **Property 1: Neue Pflanzen sind standardmäßig aktiv**
    - Zufällige Pflanzendaten → nach `add_plant()` hat die Pflanze `aktiv = 1`
    - **Validates: Requirements 1.3**

  - [x] 8.2 Property 2: Deaktivieren-Aktivieren Round-Trip
    - **Property 2: Deaktivieren-Aktivieren Round-Trip**
    - Zufällige Pflanze → deactivate setzt `aktiv = 0`, activate setzt `aktiv = 1`
    - **Validates: Requirements 2.2, 3.2**

  - [x] 8.3 Property 3: Deaktivierung bewahrt alle Daten
    - **Property 3: Deaktivierung bewahrt alle Daten (Invariante)**
    - Zufällige Pflanze mit Ereignissen/Beobachtungen → nach Deaktivierung alle Daten außer `aktiv` unverändert
    - **Validates: Requirements 2.3**

  - [x] 8.4 Property 4: Kontextabhängiger Button auf der Bearbeitungsseite
    - **Property 4: Kontextabhängiger Button auf der Bearbeitungsseite**
    - Zufällige Pflanze → Edit-Seite zeigt „Inaktiv setzen" wenn aktiv, „Aktivieren" wenn inaktiv
    - **Validates: Requirements 2.1, 3.1, 5.2**

  - [x] 8.5 Property 5: Korrektes Redirect-Verhalten nach Statusänderung
    - **Property 5: Korrektes Redirect-Verhalten nach Statusänderung**
    - Zufällige Pflanze → POST deactivate → 302 auf `/`, POST activate → 302 auf `/plant/<id>/edit`
    - **Validates: Requirements 2.4, 3.3**

  - [x] 8.6 Property 6: Filterverhalten der Pflanzenliste
    - **Property 6: Filterverhalten der Pflanzenliste**
    - Zufällige Mischung aktiv/inaktiv → GET `/` zeigt nur aktive, GET `/?show_inactive=1` zeigt alle
    - **Validates: Requirements 4.1, 4.3**

  - [x] 8.7 Property 7: Visuelle Kennzeichnung inaktiver Pflanzen
    - **Property 7: Visuelle Kennzeichnung inaktiver Pflanzen**
    - Inaktive Pflanze in Liste → `row-inactive` Klasse und Badge; Edit-Seite → Inaktiv-Hinweis
    - **Validates: Requirements 4.4, 5.1**

  - [x] 8.8 Property 8: Bearbeitungsseite funktioniert für inaktive Pflanzen
    - **Property 8: Bearbeitungsseite funktioniert für inaktive Pflanzen**
    - Inaktive Pflanze mit Daten → alle Formulare, Ereignisse, Beobachtungen, Lösch-Button vorhanden
    - **Validates: Requirements 6.1, 6.2, 6.3**

  - [x] 8.9 Property 9: Duplikat einer inaktiven Pflanze ist aktiv
    - **Property 9: Duplikat einer inaktiven Pflanze ist aktiv**
    - Inaktive Pflanze → `duplicate_plant()` → Duplikat hat `aktiv = 1`
    - **Validates: Requirements 7.1**

- [x] 9. Example-Based Tests (pytest)
  - [x] 9.1 Test: POST `/plant/99999/deactivate` → HTTP 404
    - _Requirements: 8.1_
  - [x] 9.2 Test: POST `/plant/99999/activate` → HTTP 404
    - _Requirements: 8.1_
  - [x] 9.3 Test: GET `/` enthält Checkbox „Inaktive anzeigen"
    - _Requirements: 4.2_
  - [x] 9.4 Test: Migration fügt `aktiv`-Spalte hinzu, bestehende Pflanzen erhalten `aktiv = 1`
    - _Requirements: 1.4_

- [x] 10. Final Checkpoint — Alle Tests bestehen
  - Ensure all tests pass, ask the user if questions arise.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen für Nachvollziehbarkeit
- Checkpoints stellen inkrementelle Validierung sicher
- Property Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
