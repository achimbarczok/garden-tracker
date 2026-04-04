# Implementierungsplan: Phänologischer Kalender

## Übersicht

Phänologisches Logbuch mit eigener Tabelle, Verwaltungsseite und Startseiten-Anzeige.

## Tasks

- [x] 1. Datenbank: `phaenologie`-Tabelle in `_migrate()` anlegen
- [x] 2. Datenbank: Funktionen `get_phaenologie_jahr`, `get_phaenologie_alle_jahre`, `upsert_phaenologie`, `remove_phaenologie`, `get_aktuelle_phase` implementieren
- [x] 3. Routen: `GET /phaenologie`, `POST /phaenologie/save`, `POST /phaenologie/<id>/remove` in `app.py`
- [x] 4. Template: `phaenologie.html` mit Jahresauswahl, Phasen-Tabelle, Eintragungsformular
- [x] 5. Startseite: Banner mit aktueller Phase oder "noch nicht erfasst"-Hinweis
- [x] 6. Navigation: Link im Header zu `/phaenologie`
- [x] 7. Phänologische-Phase-Freitextfeld aus Beobachtungen entfernt

## Status

Alle Tasks wurden implementiert (nachträglich dokumentiert).
