# Anforderungsdokument: Pflanze duplizieren

## Einleitung

Diese Funktion ermöglicht es, eine bestehende Pflanze im Garten-Tracker zu duplizieren. Der Anwendungsfall ist die Mehrfachaussaat derselben Pflanze zu unterschiedlichen Zeitpunkten in einer Saison (z.B. Zuckererbsen im März und April). Anstatt ein komplexes Satz-System zu implementieren, wird die Pflanze einfach kopiert und die Ereigniszeiträume am Duplikat manuell angepasst.

## Glossar

- **Pflanze**: Ein Eintrag in der `plants`-Tabelle mit allen Stammdaten (Name, Kategorie, Typ, Sorte, Lichtbedarf, Lebensdauer, Farbe, Anzahl, Pflanzmonat, Pflanzjahr, Beschreibung, Kommentar)
- **Ereignis**: Ein erwartetes saisonales Ereignis einer Pflanze (z.B. Blüte, Ernte, Vorkultur) mit Zeitraum (Startmonat, Endmonat, Start-Detail, End-Detail)
- **Beobachtung**: Eine tatsächlich beobachtete Ereigniszeiterfassung pro Jahr, spezifisch für eine einzelne Pflanzung
- **Stammdaten**: Alle Felder einer Pflanze außer Ereignissen und Beobachtungen
- **Duplikat**: Die neu erstellte Kopie einer Pflanze, die nach der Erstellung unabhängig vom Original existiert
- **Satz-Suffix**: Der automatisch generierte Namensanhang zur Unterscheidung von Duplikaten, z.B. „(2. Satz)"
- **Duplikation_Service**: Die serverseitige Logik in `db.py`, die eine Pflanze mit Ereignissen kopiert und die neue Pflanzen-ID zurückgibt
- **Bearbeitungsseite**: Die bestehende Seite unter `/plant/<id>/edit` (Template `edit.html`)

## Anforderungen

### Anforderung 1: Duplizieren-Button in der Pflanzenliste

**User Story:** Als Gärtner möchte ich in der Pflanzenliste einen Duplizieren-Button pro Pflanze sehen, damit ich eine Pflanze schnell kopieren kann.

#### Akzeptanzkriterien

1. THE Bearbeitungsseite SHALL einen „Duplizieren"-Button für die aktuell angezeigte Pflanze anzeigen.
2. WHEN der Benutzer den Duplizieren-Button betätigt, THE Bearbeitungsseite SHALL eine POST-Anfrage an den Duplikations-Endpunkt senden.

### Anforderung 2: Stammdaten kopieren

**User Story:** Als Gärtner möchte ich, dass beim Duplizieren alle Stammdaten der Pflanze übernommen werden, damit ich nicht alles neu eingeben muss.

#### Akzeptanzkriterien

1. WHEN eine Pflanze dupliziert wird, THE Duplikation_Service SHALL alle Stammdaten der Quellpflanze in die neue Pflanze kopieren: Name, Kategorie, Typ, Sorte, Lichtbedarf, Lebensdauer, Farbe, Anzahl, Pflanzmonat, Pflanzjahr, Beschreibung und Kommentar.
2. WHEN eine Pflanze dupliziert wird, THE Duplikation_Service SHALL eine neue, eigenständige Pflanzen-ID für das Duplikat erzeugen.

### Anforderung 3: Automatische Namensanpassung

**User Story:** Als Gärtner möchte ich, dass das Duplikat automatisch einen angepassten Namen erhält, damit ich Original und Kopie in der Liste unterscheiden kann.

#### Akzeptanzkriterien

1. WHEN eine Pflanze dupliziert wird und der Name der Quellpflanze kein Satz-Suffix enthält, THE Duplikation_Service SHALL den Namen des Duplikats auf „{Originalname} (2. Satz)" setzen.
2. WHEN eine Pflanze dupliziert wird und der Name der Quellpflanze bereits ein Satz-Suffix „(N. Satz)" enthält, THE Duplikation_Service SHALL den Namen des Duplikats auf „{Basisname} ({N+1}. Satz)" setzen.

### Anforderung 4: Ereignisse kopieren

**User Story:** Als Gärtner möchte ich, dass alle erwarteten Ereignisse der Quellpflanze auf das Duplikat übertragen werden, damit ich nur die Zeiträume anpassen muss.

#### Akzeptanzkriterien

1. WHEN eine Pflanze dupliziert wird, THE Duplikation_Service SHALL alle Ereignisse der Quellpflanze (Ereignistyp, Startmonat, Endmonat, Start-Detail, End-Detail) als neue Ereignisse für das Duplikat anlegen.
2. WHEN eine Pflanze dupliziert wird, THE Duplikation_Service SHALL für jedes kopierte Ereignis eine neue, eigenständige Ereignis-ID erzeugen.

### Anforderung 5: Beobachtungen ausschließen

**User Story:** Als Gärtner möchte ich, dass Beobachtungen nicht mitkopiert werden, weil diese spezifisch für eine einzelne Pflanzung sind.

#### Akzeptanzkriterien

1. WHEN eine Pflanze dupliziert wird, THE Duplikation_Service SHALL keine Beobachtungen der Quellpflanze auf das Duplikat übertragen.
2. THE Duplikat SHALL nach der Erstellung eine leere Beobachtungsliste besitzen.

### Anforderung 6: Unabhängigkeit von Original und Duplikat

**User Story:** Als Gärtner möchte ich, dass Original und Duplikat nach der Duplizierung vollständig unabhängig voneinander sind, damit Änderungen am einen den anderen nicht beeinflussen.

#### Akzeptanzkriterien

1. THE Duplikation_Service SHALL keine Fremdschlüssel-Beziehung oder Referenz zwischen Quellpflanze und Duplikat anlegen.
2. WHEN das Duplikat erstellt wurde, THE Duplikation_Service SHALL sicherstellen, dass Änderungen an der Quellpflanze keine Auswirkungen auf das Duplikat haben und umgekehrt.

### Anforderung 7: Weiterleitung zur Bearbeitungsseite

**User Story:** Als Gärtner möchte ich nach dem Duplizieren direkt auf die Bearbeitungsseite des Duplikats weitergeleitet werden, damit ich sofort die Ereigniszeiträume anpassen kann.

#### Akzeptanzkriterien

1. WHEN die Duplizierung erfolgreich abgeschlossen wurde, THE Anwendung SHALL den Benutzer zur Bearbeitungsseite des neu erstellten Duplikats weiterleiten (`/plant/<neue_id>/edit`).

### Anforderung 8: Fehlerbehandlung

**User Story:** Als Gärtner möchte ich eine verständliche Fehlermeldung erhalten, wenn die Duplizierung fehlschlägt.

#### Akzeptanzkriterien

1. IF die Quellpflanze nicht existiert, THEN THE Anwendung SHALL einen HTTP-404-Fehler zurückgeben.
2. IF ein Datenbankfehler während der Duplizierung auftritt, THEN THE Duplikation_Service SHALL keine teilweise kopierten Daten in der Datenbank hinterlassen (atomare Transaktion).
