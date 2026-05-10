# Implementation Plan: KI-Pflanzendaten

## Overview

Implementierung der KI-gestützten Autofill-Funktion für Pflanzendaten. Die Umsetzung erfolgt in logischen Schritten: zuerst das gemeinsame LLM-Modul extrahieren, dann den Autofill-Endpunkt mit Parsing/Validierung bauen, anschließend die Frontend-Integration, und zuletzt Aufräumarbeiten (Seed-Scripts entfernen, Doku aktualisieren).

## Tasks

- [x] 1. LLM-Provider in gemeinsames Modul extrahieren
  - [x] 1.1 Erstelle `llm.py` mit LLMProvider-Abstraktion
    - Extrahiere `LLMProvider` (ABC), `ClaudeProvider`, `MistralProvider` aus `monthly_report.py`
    - Implementiere `get_provider()` und `is_llm_configured()` Hilfsfunktionen
    - Umgebungsvariablen: `LLM_PROVIDER`, `LLM_MODEL`, `ANTHROPIC_API_KEY`, `MISTRAL_API_KEY`
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 1.2 Refactore `monthly_report.py` zur Nutzung von `llm.py`
    - Entferne die Provider-Klassen aus `monthly_report.py`
    - Importiere `get_provider` aus `llm.py`
    - Stelle sicher, dass der monatliche Report weiterhin funktioniert
    - _Requirements: 3.1, 3.2_

- [ ] 2. Autofill-Endpunkt implementieren
  - [x] 2.1 Implementiere `_build_autofill_prompt(name)` in `app.py`
    - Prompt enthält Pflanzennamen, erwartetes JSON-Format, gültige Enum-Werte
    - Monatswerte als Integer 1–12, Beschreibung auf Deutsch
    - Detail-Werte: "Anfang", "Mitte", "Ende" oder leer
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 2.2 Property-Test: Prompt enthält Pflanzennamen und Enum-Werte
    - **Property 5: Prompt enthält Pflanzennamen und Enum-Werte**
    - **Validates: Requirements 4.1, 4.2**

  - [x] 2.3 Implementiere `_parse_autofill_response(raw)` in `app.py`
    - Parse JSON direkt oder aus Markdown-Codeblock (```json ... ```)
    - Gib `None` zurück bei ungültigem JSON
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ]* 2.4 Property-Test: Markdown-Codeblock-Extraktion
    - **Property 2: Markdown-Codeblock-Extraktion**
    - **Validates: Requirements 5.2**

  - [ ]* 2.5 Property-Test: Ungültiges JSON wird abgelehnt
    - **Property 3: Ungültiges JSON wird abgelehnt**
    - **Validates: Requirements 5.3**

  - [x] 2.6 Implementiere `_validate_autofill_data(data)` in `app.py`
    - Validiere lichtbedarf, lebensdauer, kategorie gegen bekannte Enum-Werte
    - Filtere ungültige Ereignisse heraus (ungültiger Typ oder Monat außerhalb 1–12)
    - Setze ungültige detail-Werte auf leeren String
    - Lasse gültige Felder bestehen, leere ungültige Felder
    - _Requirements: 2.5, 5.4_

  - [ ]* 2.7 Property-Test: Validierung filtert ungültige Werte
    - **Property 4: Validierung filtert ungültige Werte**
    - **Validates: Requirements 2.5, 5.4**

  - [ ]* 2.8 Property-Test: Autofill-Daten Round-Trip
    - **Property 1: Autofill-Daten Round-Trip**
    - **Validates: Requirements 5.1, 5.5**

  - [x] 2.9 Implementiere Route `POST /api/autofill` in `app.py`
    - Prüfe ob Pflanzenname im Request vorhanden (sonst HTTP 400)
    - Rufe `get_provider().generate(prompt)` auf
    - Parse und validiere die Antwort
    - Gib strukturiertes JSON zurück (`{"ok": true, "data": {...}}` oder `{"ok": false, "error": "..."}`)
    - Fehlerbehandlung: fehlender API-Key, LLM-Fehler, ungültiges JSON
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 2.10 Unit-Tests für den Autofill-Endpunkt
    - Teste korrektes JSON-Format mit gemocktem LLM
    - Teste Fehler bei leerem Namen (HTTP 400)
    - Teste Fehler bei LLM-Exception (HTTP 502)
    - Teste Fehler bei fehlendem API-Key
    - _Requirements: 2.1, 2.3, 2.4_

- [x] 3. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 4. Frontend-Integration
  - [x] 4.1 Autofill-Button und JS in `templates/index.html` hinzufügen
    - Button „🤖 KI-Vorschlag" im Pflanze-hinzufügen-Formular
    - Button nur rendern wenn `llm_available=True` (Jinja2-Bedingung)
    - Button deaktiviert wenn Namensfeld leer (JS-Event-Listener)
    - Fetch-Aufruf an `/api/autofill` mit Ladezustand
    - Formularfelder befüllen bei Erfolg, Fehlermeldung bei Fehler
    - Ereignisse als sichtbare Vorschläge anzeigen
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 8.1, 8.2, 8.3, 8.4_

  - [x] 4.2 Autofill-Button und JS in `templates/edit.html` hinzufügen
    - Button „🤖 KI-Vorschlag" im Bearbeitungsformular
    - Button nur rendern wenn `llm_available=True`
    - Nur leere Felder befüllen, bereits ausgefüllte Felder unverändert lassen
    - Ereignisse als übernehmbare Vorschläge anzeigen (einzeln übernehm-/verwerfbar)
    - _Requirements: 6.1, 6.2, 6.3, 8.1, 8.2, 8.3, 8.4_

  - [x] 4.3 Template-Variable `llm_available` in relevanten Routes setzen
    - In den Routes für index und edit `llm_available=is_llm_configured()` an Template übergeben
    - Import von `is_llm_configured` aus `llm.py` in `app.py`
    - _Requirements: 8.4_

- [x] 5. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 6. Seed-Scripts entfernen und Dokumentation aktualisieren
  - [x] 6.1 Lösche Seed-Scripts
    - Entferne `seed_plants.py`, `seed_neue_pflanzen.py`, `seed_weitere_pflanzen.py`, `seed_wildtulpe_etc.py`
    - _Requirements: 7.1_

  - [x] 6.2 Aktualisiere Dokumentation
    - Entferne Verweise auf Seed-Scripts aus `README.md`
    - Aktualisiere `.kiro/steering/structure.md` (entferne Seed-Script-Einträge, füge `llm.py` hinzu)
    - Aktualisiere `.kiro/steering/tech.md` (entferne Seed-Befehle, füge neue Umgebungsvariablen hinzu)
    - _Requirements: 7.2_

- [x] 7. Final-Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Requirements für Nachverfolgbarkeit
- Property-Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
- Die Frontend-Integration nutzt minimales Inline-JS (kein Framework), konsistent mit dem bestehenden Projekt-Stil
- `llm.py` wird als erstes erstellt, damit alle nachfolgenden Tasks darauf aufbauen können
