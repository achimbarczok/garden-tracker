# Design: Phänologischer Kalender

## Übersicht

Eigene SQLite-Tabelle `phaenologie` mit UNIQUE(jahr, phase)-Constraint. Eigene Seite `/phaenologie` mit Jahresauswahl und Eintragungsformular. Startseite zeigt aktuelle Phase via Lookup-Funktion.

## Datenmodell

```sql
CREATE TABLE IF NOT EXISTS phaenologie (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    jahr        INTEGER NOT NULL,
    phase       TEXT    NOT NULL,
    startmonat  INTEGER NOT NULL,
    start_detail TEXT,
    endmonat    INTEGER NOT NULL,
    end_detail  TEXT,
    UNIQUE(jahr, phase)
);
```

## Komponenten

### db.py — Neue Funktionen

- `PHAENOLOGISCHE_PHASEN` — Liste der 10 festen Phasen
- `get_phaenologie_jahr(jahr)` — Alle Einträge für ein Jahr
- `get_phaenologie_alle_jahre()` — Alle Jahre mit Daten
- `upsert_phaenologie(jahr, phase, ...)` — Einfügen oder Aktualisieren
- `remove_phaenologie(id)` — Eintrag löschen
- `get_aktuelle_phase(monat, tag, jahr)` — Aktuelle Phase bestimmen

### app.py — Neue Routen

| Route | Methode | Beschreibung |
|-------|---------|--------------|
| `/phaenologie` | GET | Jahresübersicht mit Tabelle und Formular |
| `/phaenologie/save` | POST | Phase eintragen/aktualisieren |
| `/phaenologie/<id>/remove` | POST | Phase-Eintrag löschen |

### Templates

- `phaenologie.html` — Eigene Seite mit Jahresauswahl, Phasen-Tabelle, Eintragungsformular
- `index.html` — Banner mit aktueller Phase oder "noch nicht erfasst"-Hinweis
- `base.html` — Nav-Link "Phänologie" im Header

## Lookup-Algorithmus für aktuelle Phase

Detail-Werte werden in ungefähre Tage umgerechnet:
- Anfang → 5
- Mitte → 15
- Ende → 25
- kein Detail → 1

Vergleich: `monat * 100 + tag` für Start, Ende und heute. Die erste Phase deren Bereich das heutige Datum enthält wird zurückgegeben.

## Correctness Properties

### Property 1: Upsert-Idempotenz
Für jede Phase und jedes Jahr: nach zweimaligem Aufruf von `upsert_phaenologie` mit unterschiedlichen Werten soll genau ein Eintrag existieren, mit den Werten des zweiten Aufrufs.

### Property 2: Aktuelle-Phase-Konsistenz
Für jedes Datum innerhalb eines eingetragenen Phasen-Zeitraums soll `get_aktuelle_phase` den Namen dieser Phase zurückgeben.

### Property 3: Keine Phase außerhalb der Zeiträume
Für jedes Datum das in keinem eingetragenen Zeitraum liegt soll `get_aktuelle_phase` None zurückgeben.
