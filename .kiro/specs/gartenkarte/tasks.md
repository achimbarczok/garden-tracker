# Implementation Plan: Gartenkarte

## Übersicht

Erweitert den Garten-Tracker um eine visuelle Gartenkarte, auf der Pflanzen frei positioniert werden können. Umfasst zwei neue DB-Tabellen `kartenbild` und `kartenpositionen` (Migration V5), 6 neue DB-Funktionen in `db.py`, Bildverarbeitung mit Pillow (EXIF-Rotation, Verkleinerung auf max. 1920px, JPEG-Konvertierung), 5 neue Routen + Hilfsfunktionen in `app.py`, ein neues Template `gartenkarte.html`, Navigation in `base.html`, CSS-Ergänzungen und `Pillow` als bestehende Abhängigkeit.

## Tasks

- [x] 1. Datenbank-Migration und DB-Funktionen
  - [x] 1.1 Schema-Migration V5: Tabellen `kartenbild` und `kartenpositionen` in `db.py`
    - `SCHEMA_VERSION` auf 5 erhöhen
    - Neuer Block `if current < 5` in `_migrate()`:
      ```sql
      CREATE TABLE IF NOT EXISTS kartenbild (
          id        INTEGER PRIMARY KEY AUTOINCREMENT,
          dateiname TEXT    NOT NULL
      );
      CREATE TABLE IF NOT EXISTS kartenpositionen (
          id       INTEGER PRIMARY KEY AUTOINCREMENT,
          plant_id INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
          x        REAL    NOT NULL,
          y        REAL    NOT NULL
      );
      ```
    - _Requirements: 7.1, 7.2, 7.4_

  - [x] 1.2 Neue DB-Funktionen in `db.py`
    - `get_kartenbild() -> dict | None` — `SELECT id, dateiname FROM kartenbild LIMIT 1`
    - `save_kartenbild(dateiname: str) -> None` — `DELETE FROM kartenbild` + `INSERT INTO kartenbild`
    - `remove_kartenbild() -> None` — `DELETE FROM kartenpositionen` + `DELETE FROM kartenbild` (atomare Transaktion)
    - `get_kartenpositionen() -> list[dict]` — JOIN auf `plants` für Name und Farbe, ORDER BY `kp.id`
    - `add_kartenposition(plant_id: int, x: float, y: float) -> None` — INSERT
    - `remove_kartenposition(position_id: int) -> None` — DELETE
    - _Requirements: 7.1, 7.2, 7.3, 4.3, 4.6, 6.2_


- [x] 2. Checkpoint — DB-Schicht prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 3. Routen und Bildverarbeitung in `app.py`
  - [x] 3.1 Neue Imports, Konstanten und Verzeichnis-Setup in `app.py`
    - DB-Imports erweitern: `get_kartenbild`, `save_kartenbild`, `remove_kartenbild`, `get_kartenpositionen`, `add_kartenposition`, `remove_kartenposition`
    - Konstanten: `MAX_KARTE_DIMENSION = 1920`, `KARTE_DIR = Path(DB_PATH).parent / "karte"`
    - `os.makedirs(KARTE_DIR, exist_ok=True)` beim Start
    - `_safe_next()` um `/gartenkarte` erweitern
    - _Requirements: 8.1, 8.2, 9.2_

  - [x] 3.2 Hilfsfunktion `process_kartenbild(file_storage) -> bytes`
    - `Image.open()` → `ImageOps.exif_transpose()` → RGB-Konvertierung → `thumbnail((1920, 1920), Image.LANCZOS)` wenn lange Seite > 1920 → JPEG Qualität 85 in BytesIO
    - Bei `UnidentifiedImageError` oder anderen Pillow-Fehlern: Exception werfen
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 3.3 Hilfsfunktion `_render_karte_error(error, kartenbild=None, positionen=None, plants=None)`
    - Rendert `gartenkarte.html` mit Fehlermeldung und HTTP 400
    - Lädt fehlende Daten nach (kartenbild, positionen, plants) falls nicht übergeben
    - _Requirements: 11.1, 11.2, 11.3, 11.4_

  - [x] 3.4 Route `GET /gartenkarte` → `gartenkarte_page()`
    - `get_kartenbild()`, `get_kartenpositionen()`, `get_all_plants()` laden
    - Rendert `gartenkarte.html`
    - _Requirements: 1.1, 4.1, 5.1, 9.2_

  - [x] 3.5 Route `POST /gartenkarte/bild/upload` → `upload_kartenbild()`
    - Validierung: Datei vorhanden, MIME-Typ in `ALLOWED_MIME_TYPES`
    - `process_kartenbild()` aufrufen (try/except für Bildfehler)
    - Altes Kartenbild löschen: `get_kartenbild()` → falls vorhanden, Datei vom Dateisystem löschen
    - UUID-Dateiname generieren, Datei in `KARTE_DIR` schreiben
    - `save_kartenbild(dateiname)` aufrufen
    - Bei Dateisystemfehler: Fehlermeldung, kein DB-Eintrag
    - Redirect auf `/gartenkarte`
    - _Requirements: 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 3.2, 8.1, 8.2, 8.3, 11.1, 11.2_

  - [x] 3.6 Route `POST /gartenkarte/bild/remove` → `remove_kartenbild_route()`
    - `get_kartenbild()` → falls None, Redirect auf `/gartenkarte`
    - `remove_kartenbild()` — DB-Einträge löschen (kartenbild + kartenpositionen)
    - Datei vom Dateisystem löschen (Fehler ignorieren falls Datei fehlt)
    - Redirect auf `/gartenkarte`
    - _Requirements: 3.4, 3.5_

  - [x] 3.7 Route `POST /gartenkarte/position/add` → `add_position_route()`
    - Prüft ob Kartenbild vorhanden (`get_kartenbild()`)
    - Liest `plant_id`, `x`, `y` aus dem Formular
    - Validiert `plant_id` (Pflanze muss existieren) → 404 wenn nicht
    - Validiert `x` und `y` (0.0–100.0) → Fehlermeldung wenn ungültig
    - `add_kartenposition(plant_id, x, y)`
    - Redirect auf `/gartenkarte`
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 11.3, 11.4_

  - [x] 3.8 Route `POST /gartenkarte/position/<int:position_id>/remove` → `remove_position_route()`
    - `remove_kartenposition(position_id)`
    - Redirect auf `/gartenkarte`
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 3.9 Route `GET /karte/<path:dateiname>` → `serve_kartenbild()`
    - `send_from_directory(KARTE_DIR, dateiname)`
    - _Requirements: 8.1_

- [x] 4. Checkpoint — Routen prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Template, Navigation und CSS
  - [x] 5.1 Neues Template `templates/gartenkarte.html`
    - Erweitert `base.html`
    - Wenn kein Kartenbild: Upload-Formular mit Empty-State anzeigen
    - Wenn Kartenbild vorhanden: Bild mit Markierungen (CSS `position: absolute`, Prozentwerte), Pflanze-Dropdown, Ersetzen/Löschen-Buttons
    - Markierungen: farbige Punkte mit `title`-Attribut (Pflanzenname), Entfernen-Button pro Markierung
    - Minimales Inline-JavaScript: Klick-Koordinaten relativ zum Bild erfassen, in versteckte Formularfelder schreiben, Formular absenden
    - _Requirements: 1.1, 3.1, 3.3, 4.1, 4.2, 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 10.1, 10.2_

  - [x] 5.2 Navigationslink in `templates/base.html`
    - Neuer Link „🗺️ Karte" in der Header-Navigation mit `nav-active`-Klasse
    - _Requirements: 9.1, 9.3_

  - [x] 5.3 CSS-Klassen für Gartenkarte in `static/style.css`
    - `.karte-container`, `.karte-bild-wrap` (position: relative, cursor: crosshair)
    - `.karte-bild` (width: 100%, border-radius, border)
    - `.karte-marker` (position: absolute, runder Punkt, transform: translate(-50%, -50%))
    - `.marker-remove`, `.marker-remove-btn` (Hover-Lösch-Button)
    - `.karte-controls`, `.karte-hint`, `.karte-actions`
    - Mobile-Anpassungen für Bildschirme < 600px
    - _Requirements: 5.2, 5.4, 5.5, 10.1, 10.2, 10.3_

- [x] 6. Checkpoint — UI prüfen
  - Ensure all tests pass, ask the user if questions arise.


- [x] 7. Property-Based Tests (Hypothesis)
  - [x] 7.1 Property 1: Bildverkleinerung und JPEG-Konvertierung
    - **Property 1: Bildverkleinerung und JPEG-Konvertierung**
    - Zufällige Bildgrößen (1–5000 × 1–5000) → nach `process_kartenbild()`: Ergebnis ist JPEG, lange Seite = min(original, 1920), Seitenverhältnis proportional erhalten
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 7.2 Property 2: Upload speichert Kartenbild korrekt
    - **Property 2: Upload speichert Kartenbild korrekt**
    - Zufällige gültige Bilder → nach Upload: genau eine Datei in `karte/` und genau ein DB-Eintrag mit passendem Dateinamen
    - **Validates: Requirements 1.2, 8.1**

  - [x] 7.3 Property 3: Nur gültige MIME-Typen werden akzeptiert
    - **Property 3: Nur gültige MIME-Typen werden akzeptiert**
    - Zufällige ungültige MIME-Typen → Upload abgelehnt mit Fehlermeldung „Nur JPEG- und PNG-Dateien sind erlaubt."
    - **Validates: Requirements 1.4, 1.5**

  - [x] 7.4 Property 4: Kartenbild ersetzen löscht alte Datei
    - **Property 4: Kartenbild ersetzen löscht alte Datei**
    - Zwei Uploads hintereinander → alte Datei gelöscht, neue vorhanden, genau ein DB-Eintrag
    - **Validates: Requirements 3.2, 8.3**

  - [x] 7.5 Property 5: Kartenbild löschen entfernt Bild und alle Positionen
    - **Property 5: Kartenbild löschen entfernt Bild und alle Positionen**
    - Kartenbild mit 0–N Positionen → nach Löschen: keine Datei, kein DB-Eintrag in kartenbild oder kartenpositionen
    - **Validates: Requirements 3.4, 3.5**

  - [x] 7.6 Property 6: Position speichern mit korrekten Koordinaten
    - **Property 6: Position speichern mit korrekten Koordinaten**
    - Zufällige gültige Koordinaten x, y ∈ [0.0, 100.0] → korrekt in DB gespeichert mit passender plant_id
    - **Validates: Requirements 4.3, 4.4**

  - [x] 7.7 Property 7: Markierungen korrekt gerendert
    - **Property 7: Markierungen korrekt gerendert**
    - Zufällige Positionen mit Pflanzendaten → HTML enthält Marker mit korrektem `left:x%;top:y%`, `title`-Attribut und ggf. `background:farbe`
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

  - [x] 7.8 Property 8: Position entfernen löscht DB-Eintrag
    - **Property 8: Position entfernen löscht DB-Eintrag**
    - Zufällige existierende Position → nach Entfernen kein DB-Eintrag mit dieser ID
    - **Validates: Requirements 6.2**

  - [x] 7.9 Property 9: Pflanze löschen entfernt alle zugehörigen Kartenpositionen
    - **Property 9: Pflanze löschen entfernt alle zugehörigen Kartenpositionen**
    - Pflanze mit 0–N Kartenpositionen → nach Löschen keine Einträge mit dieser plant_id in kartenpositionen
    - **Validates: Requirements 6.4**

  - [x] 7.10 Property 10: Maximal ein Kartenbild-Eintrag
    - **Property 10: Maximal ein Kartenbild-Eintrag**
    - Zufällige Sequenz von Upload- und Lösch-Operationen → kartenbild-Tabelle hat immer max. 1 Zeile
    - **Validates: Requirements 7.3**

  - [x] 7.11 Property 11: Ungültige Koordinaten werden abgelehnt
    - **Property 11: Ungültige Koordinaten werden abgelehnt**
    - Zufällige Koordinaten außerhalb [0.0, 100.0] → Anfrage abgelehnt mit Fehlermeldung „Ungültige Koordinaten."
    - **Validates: Requirements 11.3**

  - [x] 7.12 Property 12: Redirect nach Karten-Operationen
    - **Property 12: Redirect nach Karten-Operationen**
    - Erfolgreiche Karten-Operationen (Upload, Löschen, Position hinzufügen/entfernen) → HTTP 302 Redirect auf `/gartenkarte`
    - **Validates: Requirements 1.3, 6.3**

- [x] 8. Example-Based Tests (pytest)
  - [x] 8.1 Test: Migration erstellt `kartenbild` und `kartenpositionen` mit korrekten Spalten
    - Nach `init_db()` existieren beide Tabellen mit den erwarteten Spalten
    - _Requirements: 7.1, 7.2, 7.4_

  - [x] 8.2 Test: Upload-Formular wenn kein Kartenbild vorhanden
    - GET `/gartenkarte` ohne Kartenbild → HTML enthält Upload-Formular mit `enctype="multipart/form-data"`
    - _Requirements: 1.1_

  - [x] 8.3 Test: Upload ohne Datei → Fehlermeldung
    - POST `/gartenkarte/bild/upload` ohne Datei → „Bitte eine Bilddatei auswählen."
    - _Requirements: 1.6_

  - [x] 8.4 Test: EXIF-Rotation wird korrekt angewendet
    - Bild mit EXIF-Orientierung → nach `process_kartenbild()` korrekte Dimensionen
    - _Requirements: 2.4_

  - [x] 8.5 Test: Ersetzen-Button vorhanden wenn Kartenbild existiert
    - GET `/gartenkarte` mit Kartenbild → HTML enthält Ersetzen-Button
    - _Requirements: 3.1_

  - [x] 8.6 Test: Löschen-Button vorhanden wenn Kartenbild existiert
    - GET `/gartenkarte` mit Kartenbild → HTML enthält Löschen-Button
    - _Requirements: 3.3_

  - [x] 8.7 Test: Dropdown zeigt aktive Pflanzen
    - GET `/gartenkarte` mit Kartenbild → HTML enthält Dropdown mit aktiven Pflanzen
    - _Requirements: 4.1_

  - [x] 8.8 Test: Nicht existierende Pflanze → 404
    - POST `/gartenkarte/position/add` mit ungültiger plant_id → HTTP 404
    - _Requirements: 4.5_

  - [x] 8.9 Test: Entfernen-Button pro Markierung vorhanden
    - GET `/gartenkarte` mit Positionen → HTML enthält Entfernen-Button pro Markierung
    - _Requirements: 6.1_

  - [x] 8.10 Test: Navigationslink vorhanden
    - GET `/` → HTML enthält Navigationslink „🗺️ Karte"
    - _Requirements: 9.1_

  - [x] 8.11 Test: Navigationslink aktiv auf Gartenkarte
    - GET `/gartenkarte` → nav-active Klasse auf Karte-Link
    - _Requirements: 9.3_

  - [x] 8.12 Test: Position ohne Kartenbild → Fehlermeldung
    - POST `/gartenkarte/position/add` ohne Kartenbild → „Bitte zuerst ein Kartenbild hochladen."
    - _Requirements: 11.4_

  - [x] 8.13 Test: Beschädigte Bilddatei → Fehlermeldung
    - POST mit beschädigter Datei → „Das Bild konnte nicht verarbeitet werden."
    - _Requirements: 11.2_

  - [x] 8.14 Test: Kartenbild-Auslieferung über `/karte/<dateiname>`
    - GET `/karte/<dateiname>` → Status 200, Bild wird ausgeliefert
    - _Requirements: 8.1_

  - [x] 8.15 Test: Dateisystemfehler hinterlässt keine partiellen DB-Einträge
    - Simulierter Dateisystemfehler beim Speichern → kein DB-Eintrag in kartenbild
    - _Requirements: 11.1_

- [x] 9. Final Checkpoint — Alle Tests bestehen
  - Ensure all tests pass, ask the user if questions arise.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen für Nachvollziehbarkeit
- Checkpoints stellen inkrementelle Validierung sicher
- Property Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
- Example-Based Tests validieren spezifische Beispiele und Randfälle
