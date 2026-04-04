# Anforderungsdokument: Pflanze inaktiv setzen

## Einleitung

Diese Funktion ermöglicht es, Pflanzen im Garten-Tracker als „inaktiv" zu markieren, anstatt sie zu löschen. Der Anwendungsfall betrifft Pflanzen, die nicht jedes Jahr gesät oder gepflegt werden, deren historische Daten (Ereignisse, Beobachtungen) aber für kommende Jahre erhalten bleiben sollen. Inaktive Pflanzen werden standardmäßig aus der Pflanzenliste ausgeblendet, können aber über einen Filter angezeigt und jederzeit wieder aktiviert werden.

## Glossar

- **Pflanze**: Ein Eintrag in der `plants`-Tabelle mit allen Stammdaten und zugehörigen Ereignissen und Beobachtungen
- **Aktiv-Status**: Ein boolesches Feld (`aktiv`) in der `plants`-Tabelle, das angibt, ob eine Pflanze aktiv (1) oder inaktiv (0) ist
- **Inaktive_Pflanze**: Eine Pflanze mit Aktiv-Status = 0, die standardmäßig in der Pflanzenliste ausgeblendet wird
- **Aktive_Pflanze**: Eine Pflanze mit Aktiv-Status = 1, die standardmäßig in der Pflanzenliste angezeigt wird
- **Pflanzenliste**: Die Hauptseite (`index.html`) mit der tabellarischen Übersicht aller Pflanzen
- **Bearbeitungsseite**: Die Detailseite einer Pflanze unter `/plant/<id>/edit` (Template `edit.html`)
- **Datenbank_Service**: Die Datenzugriffsschicht in `db.py`, die alle CRUD-Operationen auf der Datenbank ausführt
- **Anwendung**: Die Flask-Anwendung in `app.py`, die Routen, Validierung und Template-Rendering bereitstellt

## Anforderungen

### Anforderung 1: Datenbank-Feld für Aktiv-Status

**User Story:** Als Gärtner möchte ich, dass jede Pflanze einen Aktiv-Status besitzt, damit das System zwischen aktiven und inaktiven Pflanzen unterscheiden kann.

#### Akzeptanzkriterien

1. THE Datenbank_Service SHALL ein Feld `aktiv` vom Typ INTEGER (0 oder 1) in der `plants`-Tabelle bereitstellen.
2. THE Datenbank_Service SHALL den Standardwert des Feldes `aktiv` auf 1 (aktiv) setzen.
3. WHEN eine neue Pflanze hinzugefügt wird, THE Datenbank_Service SHALL den Aktiv-Status der neuen Pflanze auf 1 setzen.
4. WHEN die Datenbank migriert wird und das Feld `aktiv` noch nicht existiert, THE Datenbank_Service SHALL das Feld mit dem Standardwert 1 hinzufügen, sodass alle bestehenden Pflanzen als aktiv gelten.

### Anforderung 2: Pflanze inaktiv setzen

**User Story:** Als Gärtner möchte ich eine Pflanze auf „inaktiv" setzen können, damit ich sie aus der aktiven Liste entferne, ohne ihre Daten zu verlieren.

#### Akzeptanzkriterien

1. THE Bearbeitungsseite SHALL einen Button „Inaktiv setzen" für aktive Pflanzen anzeigen.
2. WHEN der Benutzer den Button „Inaktiv setzen" betätigt, THE Anwendung SHALL den Aktiv-Status der Pflanze auf 0 setzen.
3. WHEN eine Pflanze inaktiv gesetzt wird, THE Datenbank_Service SHALL alle Stammdaten, Ereignisse und Beobachtungen der Pflanze unverändert beibehalten.
4. WHEN eine Pflanze erfolgreich inaktiv gesetzt wurde, THE Anwendung SHALL den Benutzer zur Pflanzenliste weiterleiten.

### Anforderung 3: Pflanze reaktivieren

**User Story:** Als Gärtner möchte ich eine inaktive Pflanze wieder aktivieren können, damit ich sie in einer neuen Saison wieder verwenden kann.

#### Akzeptanzkriterien

1. THE Bearbeitungsseite SHALL einen Button „Aktivieren" für inaktive Pflanzen anzeigen.
2. WHEN der Benutzer den Button „Aktivieren" betätigt, THE Anwendung SHALL den Aktiv-Status der Pflanze auf 1 setzen.
3. WHEN eine Pflanze erfolgreich aktiviert wurde, THE Anwendung SHALL den Benutzer zur Bearbeitungsseite der Pflanze weiterleiten.

### Anforderung 4: Standardanzeige der Pflanzenliste

**User Story:** Als Gärtner möchte ich standardmäßig nur aktive Pflanzen in der Pflanzenliste sehen, damit die Übersicht übersichtlich bleibt.

#### Akzeptanzkriterien

1. THE Pflanzenliste SHALL standardmäßig nur Pflanzen mit Aktiv-Status = 1 anzeigen.
2. THE Pflanzenliste SHALL einen Filter-Schalter „Inaktive anzeigen" bereitstellen.
3. WHEN der Benutzer den Filter „Inaktive anzeigen" aktiviert, THE Pflanzenliste SHALL zusätzlich alle inaktiven Pflanzen anzeigen.
4. WHEN inaktive Pflanzen in der Liste angezeigt werden, THE Pflanzenliste SHALL inaktive Pflanzen visuell von aktiven Pflanzen unterscheidbar darstellen (z.B. durch reduzierte Deckkraft und ein Badge „inaktiv").

### Anforderung 5: Visuelle Kennzeichnung auf der Bearbeitungsseite

**User Story:** Als Gärtner möchte ich auf der Bearbeitungsseite einer inaktiven Pflanze sofort erkennen, dass diese inaktiv ist.

#### Akzeptanzkriterien

1. WHILE eine Pflanze den Aktiv-Status 0 besitzt, THE Bearbeitungsseite SHALL einen deutlich sichtbaren Hinweis „Diese Pflanze ist inaktiv" anzeigen.
2. WHILE eine Pflanze den Aktiv-Status 0 besitzt, THE Bearbeitungsseite SHALL den Button „Aktivieren" anstelle des Buttons „Inaktiv setzen" anzeigen.

### Anforderung 6: Auswirkung auf bestehende Funktionen

**User Story:** Als Gärtner möchte ich, dass inaktive Pflanzen weiterhin bearbeitbar bleiben, damit ich historische Daten korrigieren oder ergänzen kann.

#### Akzeptanzkriterien

1. WHILE eine Pflanze inaktiv ist, THE Bearbeitungsseite SHALL alle Stammdaten, Ereignisse und Beobachtungen der Pflanze weiterhin anzeigen und bearbeitbar halten.
2. WHILE eine Pflanze inaktiv ist, THE Bearbeitungsseite SHALL das Hinzufügen neuer Ereignisse und Beobachtungen weiterhin ermöglichen.
3. WHILE eine Pflanze inaktiv ist, THE Bearbeitungsseite SHALL das Löschen der Pflanze weiterhin ermöglichen.

### Anforderung 7: Duplizierung inaktiver Pflanzen

**User Story:** Als Gärtner möchte ich, dass beim Duplizieren einer inaktiven Pflanze das Duplikat als aktive Pflanze erstellt wird, damit ich die Kopie direkt verwenden kann.

#### Akzeptanzkriterien

1. WHEN eine inaktive Pflanze dupliziert wird, THE Datenbank_Service SHALL das Duplikat mit Aktiv-Status = 1 erstellen.

### Anforderung 8: Fehlerbehandlung

**User Story:** Als Gärtner möchte ich eine verständliche Rückmeldung erhalten, wenn das Ändern des Aktiv-Status fehlschlägt.

#### Akzeptanzkriterien

1. IF die Pflanze beim Ändern des Aktiv-Status nicht existiert, THEN THE Anwendung SHALL einen HTTP-404-Fehler zurückgeben.
2. IF ein Datenbankfehler beim Ändern des Aktiv-Status auftritt, THEN THE Anwendung SHALL den Benutzer zur Pflanzenliste weiterleiten, ohne den Status zu ändern.
