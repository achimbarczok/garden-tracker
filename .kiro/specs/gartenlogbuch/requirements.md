# Anforderungsdokument: Gartenlogbuch

## Einleitung

Der Garten-Tracker erhält ein eigenständiges Logbuch für gartenweite Tätigkeiten und Beobachtungen, die nicht an eine bestimmte Pflanze gebunden sind. Beispiele sind Kompost umschichten, Gartenmöbel ölen, Gartenwerkzeug reinigen oder allgemeine Gartennotizen. Die Einträge werden separat von der Pflanzenliste verwaltet und über eine eigene Seite angezeigt. Jeder Eintrag kann einer frei wählbaren Kategorie zugeordnet werden, um späteres Filtern zu ermöglichen.

## Glossar

- **Gartenlogbuch**: Neue Seite und Datenstruktur für pflanzenunabhängige Garteneinträge
- **Logbuch_Eintrag**: Ein einzelner Eintrag im Gartenlogbuch mit Datum, Titel, optionaler Kategorie und optionaler Notiz
- **Logbuch_Kategorie**: Frei eingebbarer Text zur Gruppierung von Logbuch-Einträgen (z.B. "Kompost", "Werkzeug", "Gartenmöbel", "Boden")
- **Navigation**: Hauptnavigation im Header der Anwendung

## Anforderungen

### Anforderung 1: Navigation zum Gartenlogbuch

**User Story:** Als Gärtner möchte ich das Gartenlogbuch über die Hauptnavigation erreichen, damit ich schnell zwischen Pflanzenliste und Logbuch wechseln kann.

#### Akzeptanzkriterien

1. THE Navigation SHALL einen zusätzlichen Link "📓 Logbuch" anzeigen
2. WHEN der Nutzer auf "📓 Logbuch" klickt, THE Navigation SHALL zur Gartenlogbuch-Seite unter `/logbuch` weiterleiten

### Anforderung 2: Gartenlogbuch-Seite mit Einträgen

**User Story:** Als Gärtner möchte ich alle meine gartenweiten Logbuch-Einträge chronologisch sehen, damit ich einen Überblick über erledigte Gartenarbeiten habe.

#### Akzeptanzkriterien

1. WHEN die Seite `/logbuch` aufgerufen wird, THE Gartenlogbuch SHALL alle Logbuch-Einträge anzeigen, absteigend sortiert nach Datum (neueste zuerst)
2. THE Gartenlogbuch SHALL jeden Logbuch_Eintrag mit Datum, Titel, Kategorie (falls vorhanden) und Notiz (falls vorhanden) anzeigen
3. WHEN keine Logbuch-Einträge vorhanden sind, THE Gartenlogbuch SHALL die Meldung "Noch keine Logbuch-Einträge vorhanden." anzeigen

### Anforderung 3: Logbuch-Eintrag erstellen

**User Story:** Als Gärtner möchte ich einen neuen Logbuch-Eintrag anlegen, damit ich gartenweite Tätigkeiten dokumentieren kann.

#### Akzeptanzkriterien

1. THE Gartenlogbuch SHALL ein Formular zum Erstellen eines neuen Logbuch_Eintrags anzeigen
2. THE Formular SHALL ein Pflichtfeld "Titel" enthalten
3. THE Formular SHALL ein Pflichtfeld "Datum" enthalten, vorbelegt mit dem heutigen Datum
4. THE Formular SHALL ein optionales Feld "Kategorie" enthalten
5. THE Formular SHALL ein optionales Feld "Notiz" enthalten
6. WHEN der Nutzer das Formular mit gültigem Titel und Datum absendet, THE Gartenlogbuch SHALL den Logbuch_Eintrag in der Datenbank speichern und die Logbuch-Seite neu laden
7. IF der Nutzer das Formular ohne Titel absendet, THEN THE Gartenlogbuch SHALL die Fehlermeldung "Titel darf nicht leer sein." anzeigen

### Anforderung 4: Logbuch-Eintrag löschen

**User Story:** Als Gärtner möchte ich einen Logbuch-Eintrag löschen können, damit ich fehlerhafte oder überflüssige Einträge entfernen kann.

#### Akzeptanzkriterien

1. THE Gartenlogbuch SHALL bei jedem Logbuch_Eintrag eine Schaltfläche zum Löschen anzeigen
2. WHEN der Nutzer die Lösch-Schaltfläche betätigt, THE Gartenlogbuch SHALL eine Bestätigungsabfrage anzeigen
3. WHEN der Nutzer die Löschung bestätigt, THE Gartenlogbuch SHALL den Logbuch_Eintrag aus der Datenbank entfernen und die Logbuch-Seite neu laden

### Anforderung 5: Logbuch-Eintrag bearbeiten

**User Story:** Als Gärtner möchte ich einen bestehenden Logbuch-Eintrag bearbeiten können, damit ich Korrekturen oder Ergänzungen vornehmen kann.

#### Akzeptanzkriterien

1. THE Gartenlogbuch SHALL bei jedem Logbuch_Eintrag eine Möglichkeit zum Bearbeiten anbieten (Inline-Aufklappformular)
2. WHEN der Nutzer das Bearbeitungsformular öffnet, THE Gartenlogbuch SHALL die aktuellen Werte des Logbuch_Eintrags in den Formularfeldern anzeigen
3. WHEN der Nutzer das Bearbeitungsformular mit gültigen Daten absendet, THE Gartenlogbuch SHALL den Logbuch_Eintrag in der Datenbank aktualisieren und die Logbuch-Seite neu laden
4. IF der Nutzer das Bearbeitungsformular ohne Titel absendet, THEN THE Gartenlogbuch SHALL die Fehlermeldung "Titel darf nicht leer sein." anzeigen

### Anforderung 6: Filter nach Kategorie

**User Story:** Als Gärtner möchte ich die Logbuch-Einträge nach Kategorie filtern, damit ich gezielt nach bestimmten Gartenarbeiten suchen kann (z.B. nur Kompost-Einträge).

#### Akzeptanzkriterien

1. THE Gartenlogbuch SHALL eine Filterleiste mit einem Dropdown für Kategorie anzeigen
2. THE Kategorie-Dropdown SHALL alle bisher verwendeten Kategorien als Optionen enthalten (dynamisch aus vorhandenen Einträgen ermittelt)
3. WHEN der Nutzer eine Kategorie auswählt, THE Gartenlogbuch SHALL nur Logbuch-Einträge dieser Kategorie anzeigen
4. WHEN ein Filter aktiv ist, THE Gartenlogbuch SHALL einen Link "Filter zurücksetzen" anzeigen
5. WHEN die aktiven Filter keine Ergebnisse liefern, THE Gartenlogbuch SHALL die Meldung "Keine Logbuch-Einträge gefunden." und einen Link zum Zurücksetzen des Filters anzeigen

### Anforderung 7: Datenbankschema für Logbuch-Einträge

**User Story:** Als Entwickler möchte ich, dass Logbuch-Einträge in einer eigenen Tabelle gespeichert werden, damit sie sauber von den Pflanzendaten getrennt sind.

#### Akzeptanzkriterien

1. THE Datenbank SHALL eine Tabelle `logbuch` mit den Spalten `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `datum` (TEXT NOT NULL), `titel` (TEXT NOT NULL), `kategorie` (TEXT), `notiz` (TEXT) enthalten
2. THE Datenbank SHALL die Tabelle `logbuch` über eine Schema-Migration anlegen
3. THE Tabelle `logbuch` SHALL keine Fremdschlüssel-Beziehung zur Tabelle `plants` haben

### Anforderung 8: Kategorie-Vorschläge beim Erstellen

**User Story:** Als Gärtner möchte ich beim Erstellen eines Eintrags Vorschläge für die Kategorie sehen, damit ich konsistente Kategorienamen verwende, aber trotzdem neue Kategorien frei eingeben kann.

#### Akzeptanzkriterien

1. THE Formular SHALL das Kategorie-Feld als Texteingabe mit einer `<datalist>` für Vorschläge darstellen
2. THE Datalist SHALL alle bisher verwendeten Kategorien aus vorhandenen Logbuch-Einträgen enthalten
3. THE Formular SHALL dem Nutzer erlauben, eine neue, bisher nicht verwendete Kategorie einzugeben
