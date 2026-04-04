# Implementierungsplan: Pflanze duplizieren

## Übersicht

Implementierung der Pflanzenduplikation: reine Namens-Suffix-Funktion, atomare DB-Transaktion zum Kopieren von Pflanze + Ereignissen, neue Route mit PRG-Pattern, und Duplizieren-Button auf der Bearbeitungsseite.

## Tasks

- [x] 1. Kernlogik in `db.py` implementieren
  - [x] 1.1 `generate_satz_name(name: str) -> str` implementieren
    - Reine Funktion ohne DB-Zugriff
    - Regex `r'^(.*?)\s*\((\d+)\.\s*Satz\)$'` prüft auf bestehendes Satz-Suffix
    - Ohne Suffix: `"{name} (2. Satz)"` zurückgeben
    - Mit Suffix `(N. Satz)`: `"{Basisname} ({N+1}. Satz)"` zurückgeben
    - _Anforderungen: 3.1, 3.2_

  - [ ]* 1.2 Property-Test für Satz-Suffix-Generierung
    - **Property 2: Satz-Suffix-Generierung**
    - Hypothesis-Strategie: beliebige Strings als Pflanzennamen
    - Prüft: Ergebnis enthält immer `(N. Satz)` mit N ≥ 2, Basisname bleibt erhalten, Transformation ist deterministisch
    - **Validiert: Anforderungen 3.1, 3.2**

  - [x] 1.3 `duplicate_plant(plant_id: int) -> int` implementieren
    - Liest Quellpflanze und Ereignisse in einer atomaren Transaktion
    - Erzeugt neuen Namen via `generate_satz_name()`
    - INSERT neue Pflanze mit allen Stammdaten (Name, Kategorie, Typ, Sorte, Lichtbedarf, Lebensdauer, Farbe, Anzahl, Pflanzmonat, Pflanzjahr, Beschreibung, Kommentar)
    - INSERT aller Ereignisse der Quellpflanze mit neuer `plant_id`
    - Keine Beobachtungen kopieren
    - Bei Fehler: Rollback, Exception propagieren
    - Gibt neue Pflanzen-ID zurück
    - _Anforderungen: 2.1, 2.2, 4.1, 4.2, 5.1, 5.2, 6.1, 8.2_

  - [ ]* 1.4 Property-Test für Stammdaten-Kopie
    - **Property 3: Stammdaten-Kopie mit neuer ID**
    - Hypothesis-Strategie: zufällige Pflanzendaten (alle Stammdatenfelder)
    - Prüft: Duplikat hat neue ID, alle Stammdaten außer Name identisch zum Original
    - **Validiert: Anforderungen 2.1, 2.2**

  - [ ]* 1.5 Property-Test für Ereignisse kopiert
    - **Property 4: Ereignisse kopiert mit neuen IDs**
    - Hypothesis-Strategie: Pflanze mit 0–5 zufälligen Ereignissen
    - Prüft: gleiche Anzahl Ereignisse, identische Werte (Typ, Monate, Details), neue Ereignis-IDs
    - **Validiert: Anforderungen 4.1, 4.2**

  - [ ]* 1.6 Property-Test für keine Beobachtungen im Duplikat
    - **Property 5: Keine Beobachtungen im Duplikat**
    - Hypothesis-Strategie: Pflanze mit 0–3 Beobachtungen
    - Prüft: Duplikat hat leere Beobachtungsliste
    - **Validiert: Anforderungen 5.1, 5.2**

  - [ ]* 1.7 Property-Test für Unabhängigkeit
    - **Property 6: Unabhängigkeit von Original und Duplikat**
    - Hypothesis-Strategie: zufällige Pflanze duplizieren, dann Original löschen
    - Prüft: Duplikat und seine Ereignisse existieren weiterhin unverändert
    - **Validiert: Anforderungen 6.1, 6.2**

- [x] 2. Checkpoint — Kernlogik und Property-Tests
  - Sicherstellen, dass alle bisherigen Tests bestehen. Bei Fragen den Nutzer ansprechen.

- [x] 3. Route und Template implementieren
  - [x] 3.1 `POST /plant/<int:plant_id>/duplicate` Route in `app.py`
    - `duplicate_plant` aus `db.py` importieren
    - `get_plant(plant_id)` aufrufen; `abort(404)` wenn `None`
    - `duplicate_plant(plant_id)` aufrufen
    - Bei Erfolg: `redirect` auf `/plant/<neue_id>/edit` (HTTP 302)
    - _Anforderungen: 7.1, 8.1_

  - [x] 3.2 Duplizieren-Button in `templates/edit.html`
    - POST-Formular mit `action="/plant/{{ plant.id }}/duplicate"`
    - Button: `📋 Duplizieren` mit Klasse `btn btn-outline btn-sm`
    - Platzierung: im Aktionsbereich der Bearbeitungsseite (oberhalb des Löschbereichs)
    - _Anforderungen: 1.1, 1.2_

  - [ ]* 3.3 Property-Test für Duplizieren-Button auf Bearbeitungsseite
    - **Property 1: Duplizieren-Button auf Bearbeitungsseite**
    - Hypothesis-Strategie: zufällige Pflanze anlegen, GET `/plant/<id>/edit`
    - Prüft: Response enthält Formular mit `action="/plant/<id>/duplicate"` und `method="post"`
    - **Validiert: Anforderung 1.1**

  - [ ]* 3.4 Property-Test für Weiterleitung
    - **Property 7: Weiterleitung zur Duplikat-Bearbeitungsseite**
    - Hypothesis-Strategie: zufällige Pflanze anlegen, POST `/plant/<id>/duplicate`
    - Prüft: HTTP 302, Location-Header zeigt auf `/plant/<neue_id>/edit`
    - **Validiert: Anforderung 7.1**

  - [ ]* 3.5 Example-Tests für Fehlerfälle und konkrete Beispiele
    - `test_duplicate_nonexistent_plant_404`: POST `/plant/99999/duplicate` → HTTP 404
    - `test_satz_suffix_concrete_examples`: „Zuckererbsen" → „Zuckererbsen (2. Satz)", „Tomate (2. Satz)" → „Tomate (3. Satz)"
    - `test_duplicate_form_method_is_post`: Formular hat `method="post"`
    - `test_atomic_transaction_on_failure`: Simulierter DB-Fehler → keine teilweise kopierten Daten
    - **Validiert: Anforderungen 1.2, 3.1, 3.2, 8.1, 8.2**

- [x] 4. Finaler Checkpoint — Alle Tests bestehen
  - Sicherstellen, dass alle Tests (bestehende und neue) bestehen. Bei Fragen den Nutzer ansprechen.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen zur Rückverfolgbarkeit
- Property-Tests nutzen Hypothesis mit mindestens 100 Iterationen je Property
- Alle Fehlermeldungen und UI-Texte auf Deutsch
