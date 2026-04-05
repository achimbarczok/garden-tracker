# Implementation Plan: Chronologische Listen

## Übersicht

Zwei neue pflanzenübergreifende Seiten für den Garten-Tracker: eine chronologisch sortierte Beobachtungsliste (`/beobachtungen`) und eine chronologisch sortierte Ereignisliste (`/ereignisse`). Umfasst eine reine Sortierwert-Funktion in `db.py`, zwei neue DB-Abfragen mit JOIN, zwei neue Routen in `app.py`, zwei neue Templates, Navigation-Update in `base.html` und Filter-Logik analog zur bestehenden Pflanzenübersicht.

## Tasks

- [x] 1. Sortierwert-Funktion und DB-Abfragen in `db.py`
  - [x] 1.1 Neue Funktion `berechne_sortierwert(monat, detail)` in `db.py`
    - Reine Funktion ohne DB-Zugriff
    - `monat * 100 + offset`: "Anfang" → 5, "Mitte" → 15, "Ende" → 25, None/leer → 15
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 1.2 Property-Test für Sortierwert-Berechnung
    - **Property 1: Sortierwert-Berechnung**
    - Zufälliger Monat (1–12) + Detail ("Anfang", "Mitte", "Ende", None) → korrekter Wert `monat × 100 + offset`
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

  - [x] 1.3 Neue Funktion `get_all_beobachtungen()` in `db.py`
    - JOIN `beobachtungen` mit `plants` (nur `aktiv = 1`)
    - Rückgabe: `beobachtung_id`, `plant_id`, `plant_name`, `kategorie`, `jahr`, `ereignistyp`, `startmonat`, `endmonat`, `start_detail`, `end_detail`, `notiz`, `sortierwert`
    - SQL-Sortierung: `sortierwert ASC, plant_name ASC`
    - Sortierwert via CASE-Expression in SQL berechnet
    - _Requirements: 2.1, 2.3, 2.4_

  - [x] 1.4 Neue Funktion `get_all_ereignisse()` in `db.py`
    - JOIN `ereignisse` mit `plants` (nur `aktiv = 1`)
    - Rückgabe: `ereignis_id`, `plant_id`, `plant_name`, `kategorie`, `ereignistyp`, `startmonat`, `endmonat`, `start_detail`, `end_detail`, `sortierwert`
    - SQL-Sortierung: `sortierwert ASC, plant_name ASC`
    - _Requirements: 3.1, 3.3, 3.4_

- [x] 2. Checkpoint — DB-Schicht prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Neue Routen und Navigation
  - [x] 3.1 Import-Änderung in `app.py`
    - `get_all_beobachtungen`, `get_all_ereignisse`, `berechne_sortierwert` aus `db.py` importieren
    - _Requirements: 2.1, 3.1_

  - [x] 3.2 `_safe_next()` in `app.py` erweitern
    - `/beobachtungen` und `/ereignisse` als sichere Redirect-Ziele hinzufügen
    - _Requirements: 1.2, 1.3_

  - [x] 3.3 Route `GET /beobachtungen` → `beobachtungen_page()` in `app.py`
    - `get_all_beobachtungen()` aufrufen
    - Query-Parameter: `kategorie`, `ereignis`, `monat`
    - Filter in Python (analog zu `index()`): Kategorie, Ereignistyp, Monat (startmonat ≤ fm ≤ endmonat), UND-verknüpft
    - Übergabe an Template: `beobachtungen`, `german_months`, `valid_kategorien`, `valid_ereignistypen`, Filter-Werte
    - _Requirements: 2.1, 2.2, 5.1, 5.2, 5.3, 5.4, 5.5_

  - [x] 3.4 Route `GET /ereignisse` → `ereignisse_page()` in `app.py`
    - `get_all_ereignisse()` aufrufen
    - Identische Filter-Logik wie `beobachtungen_page()`
    - Übergabe an Template: `ereignisse`, `german_months`, `valid_kategorien`, `valid_ereignistypen`, Filter-Werte
    - _Requirements: 3.1, 3.2, 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 3.5 Navigation in `templates/base.html` erweitern
    - Zwei neue Links: "🔍 Beobachtungen" → `/beobachtungen`, "🗓️ Ereignisse" → `/ereignisse`
    - Vor dem bestehenden Phänologie-Link platzieren
    - _Requirements: 1.1, 1.2, 1.3_

- [x] 4. Templates erstellen
  - [x] 4.1 Neues Template `templates/beobachtungen.html`
    - Erweitert `base.html`
    - Filterleiste mit Dropdowns für Kategorie, Ereignistyp, Monat (identisches Muster wie `index.html`)
    - Link „Filter zurücksetzen" wenn mindestens ein Filter aktiv
    - Tabelle: Pflanzenname (Link zu `/plant/<id>/edit`), Jahr, Ereignistyp, Zeitraum, Notiz
    - Leerer Zustand: „Noch keine Beobachtungen vorhanden." (ohne Filter) oder „Keine Beobachtungen gefunden." + Reset-Link (mit Filter)
    - _Requirements: 2.2, 5.1, 5.6, 7.1, 7.3, 8.1_

  - [x] 4.2 Neues Template `templates/ereignisse.html`
    - Erweitert `base.html`
    - Filterleiste mit Dropdowns für Kategorie, Ereignistyp, Monat
    - Link „Filter zurücksetzen" wenn mindestens ein Filter aktiv
    - Tabelle: Pflanzenname (Link zu `/plant/<id>/edit`), Ereignistyp, Zeitraum
    - Leerer Zustand: „Noch keine Ereignisse vorhanden." oder „Keine Ereignisse gefunden." + Reset-Link
    - _Requirements: 3.2, 6.1, 6.6, 7.2, 7.4, 8.2_

- [x] 5. Checkpoint — Templates und Routen prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Property-Based Tests (Hypothesis)
  - [x] 6.1 Property 2: Nur aktive Pflanzen in beiden Listen
    - **Property 2: Nur aktive Pflanzen in beiden Listen**
    - Zufällige Mischung aktiver/inaktiver Pflanzen mit Beobachtungen und Ereignissen → `get_all_beobachtungen()` und `get_all_ereignisse()` liefern nur Einträge aktiver Pflanzen
    - **Validates: Requirements 2.1, 3.1**

  - [x] 6.2 Property 3: Sortierung nach Sortierwert und Pflanzenname
    - **Property 3: Sortierung nach Sortierwert und Pflanzenname**
    - Zufällige Einträge → Ergebnisliste aufsteigend nach Sortierwert, bei Gleichheit alphabetisch nach Pflanzenname
    - **Validates: Requirements 2.3, 2.4, 3.3, 3.4**

  - [x] 6.3 Property 4: Beobachtungen enthalten alle Pflichtfelder und Pflanzen-Link
    - **Property 4: Beobachtungen enthalten alle Pflichtfelder und Pflanzen-Link**
    - Zufällige Beobachtungen aktiver Pflanzen → HTML enthält Pflanzenname als Link zu `/plant/<id>/edit`, Jahr, Ereignistyp, Zeitraum, Notiz
    - **Validates: Requirements 2.2, 8.1**

  - [x] 6.4 Property 5: Ereignisse enthalten alle Pflichtfelder und Pflanzen-Link
    - **Property 5: Ereignisse enthalten alle Pflichtfelder und Pflanzen-Link**
    - Zufällige Ereignisse aktiver Pflanzen → HTML enthält Pflanzenname als Link zu `/plant/<id>/edit`, Ereignistyp, Zeitraum
    - **Validates: Requirements 3.2, 8.2**

  - [x] 6.5 Property 6: Filter-Kombination auf beiden Listen
    - **Property 6: Filter-Kombination auf beiden Listen**
    - Zufällige Daten + zufällige Filter-Kombination → alle angezeigten Einträge erfüllen alle aktiven Filterkriterien gleichzeitig
    - **Validates: Requirements 5.2, 5.3, 5.4, 5.5, 6.2, 6.3, 6.4, 6.5**

- [x] 7. Example-Based Tests (pytest)
  - [x] 7.1 Test: Navigation enthält Links zu `/beobachtungen` und `/ereignisse`
    - GET `/` → HTML enthält beide Navigationslinks
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 7.2 Test: Filterleiste auf `/beobachtungen` vorhanden
    - GET `/beobachtungen` → HTML enthält Filter-Dropdowns für Kategorie, Ereignistyp, Monat
    - _Requirements: 5.1_

  - [x] 7.3 Test: Filterleiste auf `/ereignisse` vorhanden
    - GET `/ereignisse` → HTML enthält Filter-Dropdowns für Kategorie, Ereignistyp, Monat
    - _Requirements: 6.1_

  - [x] 7.4 Test: Filter-Reset-Link auf `/beobachtungen` bei aktivem Filter
    - GET `/beobachtungen?kategorie=Obst` → HTML enthält „Filter zurücksetzen"-Link
    - _Requirements: 5.6_

  - [x] 7.5 Test: Filter-Reset-Link auf `/ereignisse` bei aktivem Filter
    - GET `/ereignisse?ereignis=Ernte` → HTML enthält „Filter zurücksetzen"-Link
    - _Requirements: 6.6_

  - [x] 7.6 Test: Leerer Zustand Beobachtungen (keine Daten)
    - GET `/beobachtungen` ohne Daten → „Noch keine Beobachtungen vorhanden."
    - _Requirements: 7.1_

  - [x] 7.7 Test: Leerer Zustand Ereignisse (keine Daten)
    - GET `/ereignisse` ohne Daten → „Noch keine Ereignisse vorhanden."
    - _Requirements: 7.2_

  - [x] 7.8 Test: Keine Treffer Beobachtungen (Filter ohne Ergebnis)
    - Daten vorhanden + Filter ohne Treffer → „Keine Beobachtungen gefunden." + Reset-Link
    - _Requirements: 7.3_

  - [x] 7.9 Test: Keine Treffer Ereignisse (Filter ohne Ergebnis)
    - Daten vorhanden + Filter ohne Treffer → „Keine Ereignisse gefunden." + Reset-Link
    - _Requirements: 7.4_

- [x] 8. Final Checkpoint — Alle Tests bestehen
  - Ensure all tests pass, ask the user if questions arise.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen für Nachvollziehbarkeit
- Checkpoints stellen inkrementelle Validierung sicher
- Property Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
- Example-Based Tests validieren spezifische Beispiele und Randfälle
