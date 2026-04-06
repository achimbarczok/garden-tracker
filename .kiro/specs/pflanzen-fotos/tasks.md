# Implementation Plan: Pflanzen-Fotos

## Übersicht

Erweitert den Garten-Tracker um Foto-Upload, -Anzeige, -Löschung und Hauptbild-Verwaltung pro Pflanze. Umfasst eine neue DB-Tabelle `fotos` (Migration V3), Bildverarbeitung mit Pillow (EXIF-Rotation, Verkleinerung auf max. 640px, JPEG-Konvertierung), neue Routen in `app.py`, Erweiterung des `edit.html`-Templates um eine Foto-Galerie mit Upload-Formular, CSS-Ergänzungen und `Pillow` als neue Abhängigkeit.

## Tasks

- [x] 1. Abhängigkeit und Datenbank-Migration
  - [x] 1.1 `Pillow` in `requirements.txt` hinzufügen
    - Zeile `Pillow` ergänzen
    - _Requirements: 9.1, 9.2_

  - [x] 1.2 Schema-Migration V3: Tabelle `fotos` in `db.py`
    - `SCHEMA_VERSION` auf 3 erhöhen
    - Neuer Block `if current < 3` in `_migrate()`:
      ```sql
      CREATE TABLE IF NOT EXISTS fotos (
          id            INTEGER PRIMARY KEY AUTOINCREMENT,
          plant_id      INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
          dateiname     TEXT    NOT NULL,
          bezeichnung   TEXT,
          ist_hauptbild INTEGER DEFAULT 0
      )
      ```
    - _Requirements: 8.1, 8.2_

- [x] 2. DB-Funktionen für Foto-CRUD in `db.py`
  - [x] 2.1 Neue Funktionen `get_fotos()`, `count_fotos()`, `add_foto()`, `get_foto()`, `remove_foto()`, `set_hauptbild()`, `get_fotos_by_plant_id()`
    - `get_fotos(plant_id)` → Liste aller Fotos sortiert nach `id`
    - `count_fotos(plant_id)` → Anzahl der Fotos
    - `add_foto(plant_id, dateiname, bezeichnung, ist_hauptbild)` → neue ID; bei `ist_hauptbild=1` vorher alle anderen auf 0 setzen
    - `get_foto(foto_id)` → einzelnes Foto-Dict oder None
    - `remove_foto(foto_id)` → DELETE FROM fotos
    - `set_hauptbild(foto_id, plant_id)` → atomares UPDATE: alle auf 0, gewähltes auf 1
    - `get_fotos_by_plant_id(plant_id)` → Liste der Dateinamen (für Löschung bei Pflanze-Entfernen)
    - _Requirements: 6.3, 8.1, 11.1, 11.3, 11.7_

  - [x] 2.2 `get_plant()` erweitern: Fotos laden
    - Nach Beobachtungen zusätzlich `get_fotos(plant_id)` aufrufen und als `plant["fotos"]` anhängen
    - _Requirements: 4.1_

  - [x] 2.3 `remove_plant()` erweitern: Fotodateien löschen
    - Vor dem DELETE: `get_fotos_by_plant_id(plant_id)` aufrufen
    - Nach dem DELETE: Dateien aus `FOTOS_DIR` löschen (Fehler ignorieren)
    - `FOTOS_DIR`-Pfad aus `DB_PATH` ableiten: `Path(DB_PATH).parent / "fotos"`
    - _Requirements: 6.4_

- [x] 3. Checkpoint — DB-Schicht prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Bildverarbeitung und Routen in `app.py`
  - [x] 4.1 Neue Imports und Konstanten in `app.py`
    - Imports: `uuid`, `pathlib.Path`, `PIL.Image`, `PIL.ImageOps`, `PIL.UnidentifiedImageError`, `flask.send_from_directory`
    - DB-Imports erweitern: `add_foto`, `get_foto`, `remove_foto`, `set_hauptbild`, `count_fotos`, `get_fotos_by_plant_id`
    - Konstanten: `MAX_FOTO_SIZE = 10 * 1024 * 1024`, `MAX_FOTOS_PER_PLANT = 5`, `MAX_FOTO_DIMENSION = 640`, `FOTOS_DIR`, `ALLOWED_MIME_TYPES`
    - `app.config["MAX_CONTENT_LENGTH"] = MAX_FOTO_SIZE`
    - `os.makedirs(FOTOS_DIR, exist_ok=True)` beim Start
    - _Requirements: 7.4, 7.5, 3.1_

  - [x] 4.2 Hilfsfunktion `process_image(file_storage) -> bytes`
    - `Image.open()` → `ImageOps.exif_transpose()` → RGB-Konvertierung → `thumbnail((640, 640), Image.LANCZOS)` wenn lange Seite > 640 → JPEG Qualität 85 in BytesIO
    - Bei `UnidentifiedImageError`: Exception werfen
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 4.3 Route `POST /plant/<int:plant_id>/foto/upload`
    - Pflanze laden → 404 wenn None
    - Validierung: Datei vorhanden, MIME-Typ, Fotoanzahl < 5
    - `process_image()` aufrufen (try/except für Bildfehler)
    - UUID-Dateiname generieren, Datei in `FOTOS_DIR` schreiben
    - `ist_hauptbild = 1` wenn erstes Foto, sonst 0
    - `add_foto()` aufrufen
    - Bei Dateisystemfehler nach DB-Insert: Rollback
    - Redirect auf `/plant/<id>/edit`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.2, 3.3, 7.1, 7.2, 7.3, 10.1, 10.2, 10.3, 11.2_

  - [x] 4.4 Route `POST /foto/<int:foto_id>/remove`
    - `get_foto()` → 404 wenn None
    - `remove_foto()` → DB-Eintrag löschen
    - Datei vom Dateisystem löschen (Fehler ignorieren)
    - Redirect auf `/plant/<plant_id>/edit`
    - _Requirements: 5.1, 5.2, 5.3, 11.6_

  - [x] 4.5 Route `POST /foto/<int:foto_id>/hauptbild`
    - `get_foto()` → 404 wenn None
    - `set_hauptbild(foto_id, plant_id)`
    - Redirect auf `/plant/<plant_id>/edit`
    - _Requirements: 11.1, 11.3, 11.4_

  - [x] 4.6 Route `GET /fotos/<path:dateiname>`
    - `send_from_directory(FOTOS_DIR, dateiname)`
    - _Requirements: 4.3_

  - [x] 4.7 `edit_route()` und `_render_edit_error()` anpassen
    - `max_fotos=MAX_FOTOS_PER_PLANT` an Template übergeben
    - _Requirements: 3.2_

  - [x] 4.8 `remove()`-Route anpassen: Fotodateien löschen
    - Vor dem Löschen: `get_fotos_by_plant_id()` aufrufen
    - Nach dem DB-DELETE: Dateien löschen
    - _Requirements: 6.4_

- [x] 5. Checkpoint — Routen prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Template und CSS
  - [x] 6.1 Foto-Galerie-Abschnitt in `templates/edit.html`
    - Neuer Abschnitt „📷 Fotos" zwischen Stammdaten-Formular und Ereignisse
    - Foto-Grid mit Vorschaubildern, Bezeichnung, Hauptbild-Hervorhebung
    - Löschen-Button und Hauptbild-Button pro Foto
    - Upload-Formular mit `enctype="multipart/form-data"`, file-input und Bezeichnung-Feld
    - Hinweis wenn Maximum erreicht, Upload-Formular ausblenden
    - _Requirements: 1.1, 1.3, 3.2, 4.1, 4.2, 5.1, 11.4, 11.5_

  - [x] 6.2 CSS-Klassen für Foto-Galerie in `static/style.css`
    - `.foto-galerie` Grid-Layout
    - `.foto-item` mit Border und Radius
    - `.foto-hauptbild` mit goldenem Rahmen
    - `.foto-stern`, `.foto-bezeichnung`, `.foto-aktionen`
    - _Requirements: 4.1, 11.5_

- [x] 7. Checkpoint — UI prüfen
  - Ensure all tests pass, ask the user if questions arise.

- [x] 8. Property-Based Tests (Hypothesis)
  - [x] 8.1 Property 1: Bildverkleinerung und JPEG-Konvertierung
    - **Property 1: Bildverkleinerung und JPEG-Konvertierung**
    - Zufällige Bildgrößen (1–5000 × 1–5000) → nach `process_image()`: Ergebnis ist JPEG, lange Seite = min(original, 640), Seitenverhältnis proportional erhalten
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [x] 8.2 Property 2: Upload ordnet Foto der richtigen Pflanze zu
    - **Property 2: Upload ordnet Foto der richtigen Pflanze zu**
    - Zufällige Pflanze + gültiges Bild + optionale Bezeichnung → Foto in DB mit korrekter `plant_id` und Bezeichnung
    - **Validates: Requirements 1.2**

  - [x] 8.3 Property 3: Redirect nach Foto-Operationen
    - **Property 3: Redirect nach Foto-Operationen**
    - Upload, Löschen, Hauptbild setzen → jeweils HTTP 302 Redirect auf `/plant/<plant_id>/edit`
    - **Validates: Requirements 1.4, 5.3**

  - [x] 8.4 Property 4: Maximale Fotoanzahl pro Pflanze
    - **Property 4: Maximale Fotoanzahl pro Pflanze**
    - Pflanze mit 0–5 Fotos → Anzahl in DB nie > 5; 6. Upload wird abgelehnt
    - **Validates: Requirements 3.1, 3.3**

  - [x] 8.5 Property 5: Foto-Anzeige auf der Bearbeitungsseite
    - **Property 5: Foto-Anzeige auf der Bearbeitungsseite**
    - Pflanze mit 0–5 Fotos → HTML enthält genau so viele `<img>` wie DB-Einträge; Bezeichnungen und `foto-hauptbild`-Klasse korrekt
    - **Validates: Requirements 4.1, 4.2, 11.5**

  - [x] 8.6 Property 6: Foto-Löschung entfernt DB-Eintrag und Datei
    - **Property 6: Foto-Löschung entfernt DB-Eintrag und Datei**
    - Zufälliges Foto → nach POST `/foto/<id>/remove`: kein DB-Eintrag, keine Datei
    - **Validates: Requirements 5.2**

  - [x] 8.7 Property 7: Eindeutige Dateinamen
    - **Property 7: Eindeutige Dateinamen**
    - Mehrere Uploads hintereinander → alle generierten Dateinamen paarweise verschieden
    - **Validates: Requirements 6.2**

  - [x] 8.8 Property 8: Pflanze löschen entfernt alle zugehörigen Fotos
    - **Property 8: Pflanze löschen entfernt alle zugehörigen Fotos**
    - Pflanze mit 1–5 Fotos → nach Pflanze-Löschen: keine Foto-Dateien, keine DB-Einträge
    - **Validates: Requirements 6.4**

  - [x] 8.9 Property 9: Nur gültige MIME-Typen werden akzeptiert
    - **Property 9: Nur gültige MIME-Typen werden akzeptiert**
    - Zufällige ungültige MIME-Typen → Upload abgelehnt mit Fehlermeldung „Nur JPEG- und PNG-Dateien sind erlaubt."
    - **Validates: Requirements 7.1, 7.2**

  - [x] 8.10 Property 10: Hauptbild-Invariante
    - **Property 10: Hauptbild-Invariante — maximal ein Hauptbild pro Pflanze**
    - Zufällige Sequenz von Hauptbild-Setzungen → zu jedem Zeitpunkt max. 1 Foto mit `ist_hauptbild = 1`
    - **Validates: Requirements 11.1, 11.3**

  - [x] 8.11 Property 11: Erstes Foto wird automatisch Hauptbild
    - **Property 11: Erstes Foto wird automatisch Hauptbild**
    - Pflanze ohne Fotos → nach erstem Upload: `ist_hauptbild = 1`
    - **Validates: Requirements 11.2**

  - [x] 8.12 Property 12: Kein automatisches Hauptbild nach Löschen
    - **Property 12: Kein automatisches Hauptbild nach Löschen**
    - Pflanze mit ≥ 2 Fotos → nach Löschen des Hauptbilds: kein anderes Foto hat `ist_hauptbild = 1`
    - **Validates: Requirements 11.6**

- [x] 9. Example-Based Tests (pytest)
  - [x] 9.1 Test: Migration erstellt `fotos`-Tabelle mit korrekten Spalten
    - Nach `init_db()` existiert Tabelle `fotos` mit Spalten `id`, `plant_id`, `dateiname`, `bezeichnung`, `ist_hauptbild`
    - _Requirements: 8.1, 8.2_

  - [x] 9.2 Test: Upload-Formular auf Bearbeitungsseite vorhanden
    - GET `/plant/<id>/edit` → HTML enthält `enctype="multipart/form-data"`, file-input, Bezeichnung-Feld
    - _Requirements: 1.1, 1.3_

  - [x] 9.3 Test: Upload-Formular ausgeblendet bei 5 Fotos
    - Pflanze mit 5 Fotos → kein Upload-Formular, Hinweis „Maximum von 5 Fotos erreicht"
    - _Requirements: 3.2_

  - [x] 9.4 Test: Löschen-Button pro Foto vorhanden
    - Pflanze mit Fotos → HTML enthält Löschen-Buttons
    - _Requirements: 5.1_

  - [x] 9.5 Test: Hauptbild-Button vorhanden
    - Pflanze mit mehreren Fotos → Hauptbild-Buttons für Nicht-Hauptbilder vorhanden
    - _Requirements: 11.4_

  - [x] 9.6 Test: Upload für nicht existierende Pflanze → 404
    - POST `/plant/99999/foto/upload` → HTTP 404
    - _Requirements: 10.1_

  - [x] 9.7 Test: Upload ohne Datei → Fehlermeldung
    - POST ohne Datei → „Bitte eine Bilddatei auswählen."
    - _Requirements: 7.3_

  - [x] 9.8 Test: Beschädigte Bilddatei → Fehlermeldung
    - POST mit ungültiger Datei → „Das Bild konnte nicht verarbeitet werden."
    - _Requirements: 10.3_

  - [x] 9.9 Test: EXIF-Rotation wird korrekt angewendet
    - Bild mit EXIF-Orientierung → nach `process_image()` korrekte Dimensionen
    - _Requirements: 2.4_

  - [x] 9.10 Test: Foto-Auslieferung über `/fotos/<dateiname>`
    - GET `/fotos/<dateiname>` → Status 200, Bild wird ausgeliefert
    - _Requirements: 4.3_

  - [x] 9.11 Test: Dateisystemfehler hinterlässt keine partiellen DB-Einträge
    - Simulierter Dateisystemfehler → kein DB-Eintrag für das Foto
    - _Requirements: 10.2_

- [x] 10. Final Checkpoint — Alle Tests bestehen
  - Ensure all tests pass, ask the user if questions arise.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen für Nachvollziehbarkeit
- Checkpoints stellen inkrementelle Validierung sicher
- Property Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
- Example-Based Tests validieren spezifische Beispiele und Randfälle
