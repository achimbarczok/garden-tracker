# Requirements Document

## Introduction

Beim Anlegen neuer Pflanzen in der Web-UI soll der Benutzer optional die Pflanzendaten (Beschreibung, Blütezeit, Erntezeit, Rückschnitt etc.) per KI automatisch ausfüllen lassen können. Dazu wird dasselbe LLM genutzt, das bereits für den monatlichen Newsletter verwendet wird. Die bestehenden Seed-Scripts werden entfernt, da die KI-Autofill-Funktion sie ersetzt.

## Glossary

- **Autofill_Service**: Das Backend-Modul, das den LLM-Aufruf für das automatische Ausfüllen von Pflanzendaten durchführt
- **LLM_Provider**: Die abstrakte Schnittstelle zu einem Large Language Model (Claude oder Mistral), konfiguriert über Umgebungsvariablen
- **Pflanzendaten**: Die Gesamtheit der Felder einer Pflanze: Beschreibung, Typ, Sorte, Lichtbedarf, Lebensdauer, Kategorie und Ereignisse (Blütezeit, Erntezeit, Rückschnitt etc.)
- **Ereignis**: Ein geplanter Jahresplan-Eintrag für eine Pflanze mit Typ (Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat), Startmonat, Endmonat und optionalem Detail (Anfang/Mitte/Ende)
- **Formular**: Das HTML-Formular zum Anlegen oder Bearbeiten einer Pflanze in der Web-UI (index.html bzw. edit.html)
- **Seed_Scripts**: Die bestehenden Python-Skripte (seed_plants.py, seed_neue_pflanzen.py, seed_weitere_pflanzen.py, seed_wildtulpe_etc.py), die Pflanzendaten manuell in die Datenbank eintragen

## Requirements

### Requirement 1: KI-Autofill-Button im Formular

**User Story:** Als Benutzer möchte ich beim Anlegen einer neuen Pflanze einen Button haben, der die Pflanzendaten per KI automatisch ausfüllt, damit ich nicht alle Informationen selbst recherchieren muss.

#### Acceptance Criteria

1. WHEN der Benutzer einen Pflanzennamen eingegeben hat und den KI-Autofill-Button betätigt, THE Formular SHALL einen POST-Request an den Autofill_Service senden
2. WHEN der Autofill_Service eine erfolgreiche Antwort liefert, THE Formular SHALL die zurückgegebenen Felder (Beschreibung, Typ, Sorte, Lichtbedarf, Lebensdauer, Kategorie) in die entsprechenden Formularfelder eintragen
3. WHEN der Autofill_Service eine erfolgreiche Antwort mit Ereignissen liefert, THE Formular SHALL die vorgeschlagenen Ereignisse sichtbar anzeigen, sodass der Benutzer sie beim Speichern übernehmen kann
4. WHILE kein Pflanzenname eingegeben ist, THE Formular SHALL den KI-Autofill-Button deaktiviert darstellen
5. THE Formular SHALL den KI-Autofill-Button mit einem eindeutigen Label (z.B. „🤖 KI-Vorschlag") versehen

### Requirement 2: Autofill-Endpunkt im Backend

**User Story:** Als System möchte ich einen Backend-Endpunkt bereitstellen, der den Pflanzennamen entgegennimmt und per LLM strukturierte Pflanzendaten zurückgibt, damit das Formular diese Daten anzeigen kann.

#### Acceptance Criteria

1. WHEN ein POST-Request mit einem Pflanzennamen am Autofill-Endpunkt eingeht, THE Autofill_Service SHALL den konfigurierten LLM_Provider aufrufen und strukturierte Pflanzendaten zurückgeben
2. THE Autofill_Service SHALL die LLM-Antwort in ein strukturiertes Format parsen, das die Felder Beschreibung, Typ, Sorte, Lichtbedarf, Lebensdauer, Kategorie und eine Liste von Ereignissen enthält
3. WHEN der LLM_Provider einen Fehler zurückgibt, THE Autofill_Service SHALL eine verständliche deutsche Fehlermeldung an das Formular zurückgeben
4. WHEN kein API-Key konfiguriert ist, THE Autofill_Service SHALL eine Fehlermeldung zurückgeben, die auf die fehlende Konfiguration hinweist
5. THE Autofill_Service SHALL die Pflanzendaten validieren, sodass nur gültige Werte für Lichtbedarf (Sonne, Halbschatten, Schatten), Lebensdauer (Einjährig, Zweijährig, Mehrjährig), Kategorie und Ereignistypen zurückgegeben werden

### Requirement 3: Gemeinsame LLM-Konfiguration

**User Story:** Als Administrator möchte ich die LLM-Konfiguration (Provider, Modell, API-Key) zentral verwalten, damit sowohl der monatliche Newsletter als auch die KI-Autofill-Funktion dieselbe Konfiguration nutzen.

#### Acceptance Criteria

1. THE Autofill_Service SHALL dieselben Umgebungsvariablen (LLM_PROVIDER, LLM_MODEL, ANTHROPIC_API_KEY, MISTRAL_API_KEY) verwenden wie der monatliche Newsletter
2. THE Autofill_Service SHALL die bestehende LLM-Provider-Abstraktion (LLMProvider, ClaudeProvider, MistralProvider) wiederverwenden
3. WHEN LLM_PROVIDER auf "claude" gesetzt ist, THE Autofill_Service SHALL den ClaudeProvider verwenden
4. WHEN LLM_PROVIDER auf "mistral" gesetzt ist, THE Autofill_Service SHALL den MistralProvider verwenden

### Requirement 4: LLM-Prompt für Pflanzendaten

**User Story:** Als System möchte ich einen spezialisierten Prompt verwenden, der das LLM anweist, strukturierte und korrekte Pflanzendaten auf Deutsch zurückzugeben, damit die Autofill-Ergebnisse direkt verwendbar sind.

#### Acceptance Criteria

1. THE Autofill_Service SHALL einen Prompt an das LLM senden, der den Pflanzennamen enthält und explizit ein strukturiertes Ausgabeformat (JSON) anfordert
2. THE Autofill_Service SHALL im Prompt die gültigen Werte für Lichtbedarf, Lebensdauer, Kategorie und Ereignistypen vorgeben
3. THE Autofill_Service SHALL im Prompt angeben, dass Monatswerte als Ganzzahlen (1–12) und Ereignisse mit Start- und Endmonat zurückgegeben werden sollen
4. THE Autofill_Service SHALL im Prompt verlangen, dass die Beschreibung auf Deutsch verfasst wird und gartenrelevante Informationen (Standort, Pflege, Schnitt) enthält

### Requirement 5: LLM-Antwort-Parsing

**User Story:** Als System möchte ich die LLM-Antwort zuverlässig parsen, damit auch bei leicht abweichendem Format die Pflanzendaten korrekt extrahiert werden.

#### Acceptance Criteria

1. WHEN die LLM-Antwort gültiges JSON enthält, THE Autofill_Service SHALL die Pflanzendaten daraus extrahieren
2. WHEN die LLM-Antwort JSON in einem Markdown-Codeblock enthält, THE Autofill_Service SHALL den JSON-Inhalt aus dem Codeblock extrahieren
3. IF die LLM-Antwort kein gültiges JSON enthält, THEN THE Autofill_Service SHALL eine Fehlermeldung zurückgeben
4. THE Autofill_Service SHALL ungültige Feldwerte (z.B. unbekannte Kategorie) herausfiltern statt die gesamte Antwort zu verwerfen
5. FOR ALL gültigen Pflanzennamen, Parsen dann Serialisieren dann erneutes Parsen der Autofill-Antwort SHALL ein äquivalentes Objekt ergeben (Round-Trip-Eigenschaft)

### Requirement 6: Autofill auf der Bearbeitungsseite

**User Story:** Als Benutzer möchte ich auch auf der Bearbeitungsseite einer bestehenden Pflanze die KI-Autofill-Funktion nutzen können, damit ich nachträglich Daten ergänzen kann.

#### Acceptance Criteria

1. WHEN der Benutzer auf der Bearbeitungsseite den KI-Autofill-Button betätigt, THE Formular SHALL den aktuellen Pflanzennamen an den Autofill_Service senden
2. WHEN der Autofill_Service eine erfolgreiche Antwort liefert, THE Formular SHALL die leeren Felder mit den vorgeschlagenen Werten befüllen und bereits ausgefüllte Felder unverändert lassen
3. WHEN der Autofill_Service Ereignisse vorschlägt, THE Formular SHALL diese als Vorschläge anzeigen, die der Benutzer einzeln übernehmen oder verwerfen kann

### Requirement 7: Entfernung der Seed-Scripts

**User Story:** Als Entwickler möchte ich die Seed-Scripts entfernen, da die KI-Autofill-Funktion deren Zweck (Pflanzendaten recherchieren und eintragen) ersetzt.

#### Acceptance Criteria

1. THE Repository SHALL die Dateien seed_plants.py, seed_neue_pflanzen.py, seed_weitere_pflanzen.py und seed_wildtulpe_etc.py nicht mehr enthalten
2. THE Dokumentation (README.md, Steering-Files) SHALL keine Verweise auf die Seed-Scripts mehr enthalten

### Requirement 8: Benutzerfreundlichkeit und Feedback

**User Story:** Als Benutzer möchte ich während des KI-Aufrufs visuelles Feedback erhalten, damit ich weiß, dass die Anfrage verarbeitet wird.

#### Acceptance Criteria

1. WHILE der Autofill_Service die Anfrage verarbeitet, THE Formular SHALL einen Ladezustand anzeigen (z.B. deaktivierter Button mit Ladetext)
2. WHEN der Autofill_Service einen Fehler zurückgibt, THE Formular SHALL die Fehlermeldung dem Benutzer sichtbar anzeigen
3. WHEN der Autofill_Service erfolgreich Daten zurückgibt, THE Formular SHALL dem Benutzer signalisieren, dass die Felder befüllt wurden (z.B. kurze Erfolgsmeldung)
4. THE Formular SHALL den KI-Autofill-Button nur anzeigen, WHEN die LLM-Konfiguration serverseitig verfügbar ist (API-Key gesetzt)
