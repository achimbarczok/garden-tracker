# Implementation Plan: UI-Konsistenz-Verbesserungen

## Übersicht

Drei zusammenhängende Änderungen für ein einheitliches Erscheinungsbild: (1) `p.farbe` in den DB-Abfragen `get_all_beobachtungen()` und `get_all_ereignisse()` ergänzen, (2) Farbkreise in `beobachtungen.html` und `ereignisse.html` sowie Pflanzennamen als Links auf `index.html`, (3) neue Route `POST /ereignis/add` mit Ereignis-Formular auf der Tagebuchseite, (4) Link-Styling in Tabellenzellen.

## Tasks

- [x] 1. DB-Abfragen erweitern (`db.py`)
  - [x] 1.1 `p.farbe` zum SELECT in `get_all_beobachtungen()` hinzufügen
    - Feld `p.farbe` in die SELECT-Klausel aufnehmen, sodass jedes Ergebnis-Dict ein `farbe`-Feld enthält
    - _Requirements: 1.1, 1.4_

  - [x] 1.2 `p.farbe` zum SELECT in `get_all_ereignisse()` hinzufügen
    - Feld `p.farbe` in die SELECT-Klausel aufnehmen, sodass jedes Ergebnis-Dict ein `farbe`-Feld enthält
    - _Requirements: 1.2, 1.4_

  - [x] 1.3 Property-Test: Farbe-Feld in Beobachtungen und Ereignissen
    - **Property 1: Farbe-Feld in Beobachtungen und Ereignissen**
    - Generiert Pflanzen mit/ohne Farbe + Beobachtungen/Ereignisse, prüft dass `farbe`-Feld in DB-Abfragen dem Pflanzenwert entspricht
    - Testdatei: `tests/test_ui_konsistenz_properties.py`
    - **Validates: Requirements 1.1, 1.2, 1.4**

- [x] 2. Checkpoint — DB-Schicht prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Template-Änderungen: Farbkreise und Links
  - [x] 3.1 Farbkreis vor Pflanzennamen in `beobachtungen.html`
    - In der Tabellenzelle `<td>` den bestehenden `<a>`-Link um einen `<span class="color-dot">` erweitern: `{% if b.farbe %}<span class="color-dot" style="background:{{ b.farbe }}"></span>{% endif %}`
    - _Requirements: 1.1, 1.3, 1.4_

  - [x] 3.2 Farbkreis vor Pflanzennamen in `ereignisse.html`
    - In der Tabellenzelle `<td>` den bestehenden `<a>`-Link um einen `<span class="color-dot">` erweitern: `{% if e.farbe %}<span class="color-dot" style="background:{{ e.farbe }}"></span>{% endif %}`
    - _Requirements: 1.2, 1.3, 1.4_

  - [x] 3.3 Pflanzennamen auf `index.html` als Link zur Detailseite
    - Farbkreis + `<strong>{{ plant.name }}</strong>` gemeinsam in einen `<a href="/plant/{{ plant.id }}/edit">` wrappen
    - Bestehender Bearbeiten-Button (✏️) in der Aktionsspalte bleibt unverändert
    - _Requirements: 2.1, 2.2, 2.3_

  - [x] 3.4 Link-Styling in Tabellenzellen (`style.css`)
    - Links in `td` sollen Textfarbe erben und nur bei Hover unterstrichen werden, damit der Farbkreis visuell nicht gestört wird
    - _Requirements: 1.3, 2.2_

  - [x] 3.5 Beispiel-Tests für Farbkreise und Links
    - Testdatei: `tests/test_ui_konsistenz.py`
    - Farbkreis im HTML-Output von `/beobachtungen` und `/ereignisse` vorhanden (1.1, 1.2)
    - Kein Farbkreis wenn Pflanze keine Farbe hat (1.4)
    - Pflanzenname auf Startseite ist Link zu `/plant/<id>/edit` (2.1)
    - Farbkreis und Name im selben `<a>`-Tag (2.2)
    - Bearbeiten-Button (✏️) weiterhin in Aktionsspalte (2.3)
    - _Requirements: 1.1, 1.2, 1.4, 2.1, 2.2, 2.3_

- [x] 4. Checkpoint — Templates und Styling prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Neue Route und Formular: Ereignis über Tagebuchseite eintragen
  - [x] 5.1 Hilfsfunktion `_render_beobachtungen_error()` in `app.py`
    - Analog zu `_render_index_error()`: rendert `beobachtungen.html` mit Fehlermeldung und HTTP 400
    - Muss alle Template-Variablen übergeben (beobachtungen, plants, german_months, valid_kategorien, valid_ereignistypen, zeitraum_ereignistypen, Filter-Werte)
    - _Requirements: 3.6, 3.7_

  - [x] 5.2 Route `POST /ereignis/add` in `app.py`
    - Liest `plant_id` aus `request.form`, validiert Pflanze existiert und aktiv ist
    - Validiert Ereignistyp, Monate (1–12), Start-/End-Detail
    - Bei Zeitraum-Ereignissen (Blüte, Ernte): prüft Startmonat ≤ Endmonat
    - Bei Nicht-Zeitraum-Ereignissen: setzt Endmonat = Startmonat, End-Detail = Start-Detail
    - Speichert via `add_ereignis()` und redirected zu `/beobachtungen`
    - Fehlerbehandlung gemäß Design-Dokument (fehlende plant_id, ungültige plant_id, inaktive Pflanze, ungültiger Ereignistyp, ungültiger Monat, Startmonat > Endmonat)
    - _Requirements: 3.5, 3.6, 3.7_

  - [x] 5.3 `beobachtungen_page()` erweitern: Pflanzenliste und Ereignistypen an Template übergeben
    - `plants = get_all_plants()` für das Pflanzen-Dropdown
    - `zeitraum_ereignistypen` für JS-Toggle der Bis-Felder
    - _Requirements: 3.1, 3.2_

  - [x] 5.4 Ereignis-Formular in `beobachtungen.html`
    - Neues Card-Element unterhalb der Tabelle mit Überschrift „🗓️ Ereignis hinzufügen"
    - Pflanzen-Dropdown (alle aktiven Pflanzen), Ereignistyp-Select, Start-Detail, Startmonat, End-Detail, Endmonat (Bis-Felder per JS ein-/ausblenden), Submit-Button
    - Formular postet an `/ereignis/add`
    - Fehlermeldung via `{{ error }}` anzeigen (analog zu index.html)
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 5.5 `/ereignis/add` in `_safe_next()` als erlaubten Pfad aufnehmen
    - Nicht nötig, da die Route selbst redirected — aber `/beobachtungen` ist bereits erlaubt
    - Prüfen, dass `Pflege` als Ereignistyp im Formular enthalten ist (8 Typen)
    - _Requirements: 3.3_

  - [x] 5.6 Property-Test: Nur aktive Pflanzen im Ereignis-Dropdown
    - **Property 2: Nur aktive Pflanzen im Ereignis-Dropdown**
    - Generiert aktive/inaktive Pflanzen, prüft GET `/beobachtungen` HTML-Output
    - Testdatei: `tests/test_ui_konsistenz_properties.py`
    - **Validates: Requirements 3.2**

  - [x] 5.7 Property-Test: Gültiges Ereignis wird über Tagebuchseite gespeichert
    - **Property 3: Gültiges Ereignis wird gespeichert**
    - Generiert gültige Ereignis-Daten (aktive Pflanze, gültiger Ereignistyp, Monate 1–12), prüft POST `/ereignis/add` speichert korrekt
    - Testdatei: `tests/test_ui_konsistenz_properties.py`
    - **Validates: Requirements 3.5**

  - [x] 5.8 Property-Test: Ungültiger Ereignistyp wird abgelehnt
    - **Property 4: Ungültiger Ereignistyp wird abgelehnt**
    - Generiert ungültige Ereignistyp-Strings (nicht in VALID_EREIGNISTYPEN), prüft Ablehnung mit Fehlermeldung
    - Testdatei: `tests/test_ui_konsistenz_properties.py`
    - **Validates: Requirements 3.7**

  - [x] 5.9 Beispiel-Tests für Ereignis-Formular
    - Testdatei: `tests/test_ui_konsistenz.py`
    - Ereignis-Formular auf Tagebuchseite vorhanden (3.1)
    - Formular enthält alle erwarteten Felder (3.3)
    - Fehlermeldung bei fehlender Pflanze (3.6)
    - _Requirements: 3.1, 3.3, 3.6_

- [x] 6. Final-Checkpoint — Alle Tests bestehen
  - Ensure all tests pass, ask the user if questions arise.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen für Nachvollziehbarkeit
- Checkpoints stellen inkrementelle Validierung sicher
- Property-Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
- Beispiel-Tests validieren spezifische Szenarien und Randfälle
