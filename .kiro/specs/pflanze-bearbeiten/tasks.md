# Implementierungsplan: Pflanze bearbeiten & Mobiles Interface

## Überblick

Erweiterung des Garten-Trackers um eine Bearbeitungsseite für einzelne Pflanzen (`/plant/<id>/edit`) sowie ein responsives, mobilfreundliches CSS-Layout.

## Tasks

- [x] 1. Datenbankfunktionen erweitern (`db.py`)
  - [x] 1.1 `get_plant(plant_id: int) -> dict | None` implementieren
    - Liest eine einzelne Pflanze mit ihren Ereignissen aus der Datenbank.
    - Gibt `None` zurück, wenn keine Pflanze mit der ID existiert.
    - _Anforderungen: 2.1, 2.3, 2.5_
  - [x] 1.2 `update_plant(plant_id, name, type, variety, lichtbedarf, kommentar) -> None` implementieren
    - Aktualisiert alle Felder einer Pflanze per `UPDATE`-Statement.
    - _Anforderungen: 3.1, 3.6_

- [x] 2. Neue Routen in `app.py` hinzufügen
  - [x] 2.1 `GET /plant/<int:plant_id>/edit` → `edit_route()` implementieren
    - Ruft `get_plant(plant_id)` auf; gibt `abort(404)` zurück wenn `None`.
    - Rendert `edit.html` mit `plant`, `german_months`, `VALID_EREIGNISTYPEN`.
    - _Anforderungen: 2.1, 2.2, 2.3, 2.4, 2.5_
  - [x] 2.2 `POST /plant/<int:plant_id>/edit` → `edit_save()` implementieren
    - Validiert `name`, `type`, `lichtbedarf`.
    - Ruft `update_plant(...)` auf und leitet bei Erfolg auf `url_for("index")` weiter.
    - Gibt bei Fehler `edit.html` mit HTTP 400 und `error`-Variable zurück.
    - Gibt `abort(404)` zurück wenn Pflanze nicht existiert.
    - _Anforderungen: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

- [x] 3. `next`-Parameter in Ereignis-Routen einbauen (`app.py`)
  - [x] 3.1 `POST /plant/<id>/ereignis/add` anpassen
    - Liest optionalen Hidden-Field `next` aus dem Formular.
    - Leitet nach Erfolg auf `next` weiter, wenn er mit `/plant/` beginnt oder gleich `/` ist; sonst auf `url_for("index")`.
    - _Anforderungen: 4.1, 4.3, 4.4_
  - [x] 3.2 `POST /ereignis/<id>/remove` anpassen
    - Liest optionalen Hidden-Field `next` aus dem Formular.
    - Leitet nach Erfolg auf `next` weiter (mit gleicher Sicherheitsprüfung); sonst auf `url_for("index")`.
    - _Anforderungen: 4.2_

- [x] 4. Checkpoint — Alle bisherigen Tests bestehen
  - Sicherstellen, dass alle Tests bestehen. Bei Fragen den Nutzer ansprechen.

- [x] 5. Template `edit.html` erstellen
  - [x] 5.1 Grundstruktur von `edit.html` anlegen
    - Erweitert `base.html`.
    - Formular mit vorausgefüllten Werten für name, type, variety, lichtbedarf, kommentar.
    - Link zurück zur Pflanzenliste.
    - _Anforderungen: 2.1, 2.4_
  - [x] 5.2 Ereignisanzeige und -verwaltung in `edit.html` einbauen
    - Alle Ereignisse anzeigen mit deutschen Monatsnamen.
    - Entfernen-Schaltfläche mit Hidden-Field `next=/plant/{{ plant.id }}/edit`.
    - Formular zum Hinzufügen mit Hidden-Field `next=/plant/{{ plant.id }}/edit`.
    - _Anforderungen: 2.3, 2.4, 2.5, 4.1, 4.2_

- [x] 6. `index.html` und `base.html` anpassen
  - [x] 6.1 Bearbeiten-Link in `index.html` hinzufügen
    - `<a href="/plant/{{ plant.id }}/edit">Bearbeiten</a>` in der Aktionsspalte.
    - _Anforderungen: 1.1, 1.2_
  - [x] 6.2 CSS-Klassen für mobile Spalten in `index.html` setzen
    - `class="hide-mobile"` auf Sorte, Kommentar, Ereignisse und „Ereignis hinzufügen".
    - _Anforderungen: 5.1, 5.2_
  - [x] 6.3 Viewport-Meta-Tag in `base.html` hinzufügen
    - `<meta name="viewport" content="width=device-width, initial-scale=1">` im `<head>`.
    - _Anforderungen: 5.4_

- [x] 7. Responsives CSS in `style.css` ergänzen
  - [x] 7.1 Media Query und `.hide-mobile` implementieren
    - `@media (max-width: 599px)` mit `.hide-mobile { display: none; }`.
    - _Anforderungen: 5.1, 5.2_
  - [x] 7.2 Kartenlayout für Mobilgeräte implementieren
    - `table`, `thead`, `tbody`, `tr`, `th`, `td` als Block-Elemente im Media Query.
    - Jede `tr` als Karte mit Border und Padding.
    - _Anforderungen: 5.3_
  - [x] 7.3 Touch-freundliche Bedienelemente implementieren
    - `min-height: 44px` für `button`, `a`, `select`, `input` im Media Query.
    - `input, select, textarea { width: 100%; }` für Formularfelder.
    - _Anforderungen: 6.1, 6.2, 6.3_

- [x] 8. Finaler Checkpoint — Alle Tests bestehen
  - Sicherstellen, dass alle Tests bestehen. Bei Fragen den Nutzer ansprechen.

## Hinweise

- Jeder Task referenziert spezifische Anforderungen für Rückverfolgbarkeit.
- Der `next`-Parameter wird nur akzeptiert, wenn er mit `/plant/` beginnt oder gleich `/` ist (Open-Redirect-Schutz).
