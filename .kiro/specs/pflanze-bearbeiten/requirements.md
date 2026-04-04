# Anforderungsdokument: Pflanze bearbeiten & Mobiles Interface

## Einleitung

Diese Erweiterung des Garten-Trackers fügt zwei zusammenhängende Funktionen hinzu:

1. **Pflanze bearbeiten**: Jede Pflanze in der Liste erhält einen „Bearbeiten"-Link, der zu einer Detailseite führt. Dort können alle Felder der Pflanze bearbeitet und gespeichert werden. Die Detailseite zeigt außerdem die Ereignisse der Pflanze und erlaubt das Hinzufügen und Entfernen von Ereignissen.

2. **Mobiles Interface**: Die Pflanzenliste wird auf kleinen Bildschirmen kompakt dargestellt (nur Name, Typ, Lichtbedarf). Die Detailseite ist der Ort für vollständige Informationen und Bearbeitung auf Mobilgeräten. Das Design ist rein CSS-basiert (keine JavaScript-Frameworks), mit Touch-freundlichen Bedienelementen.

## Glossar

- **Pflanze**: Ein Datensatz in der Datenbank mit den Feldern id, name, type, variety, lichtbedarf, kommentar.
- **Ereignis**: Ein saisonales Ereignis einer Pflanze (Blüte, Ernte, Düngen, Rückschnitt) mit Start- und Endmonat.
- **Bearbeitungsseite**: Die Seite unter `/plant/<id>/edit`, auf der eine Pflanze angezeigt und bearbeitet werden kann.
- **Pflanzenliste**: Die Hauptseite (`/`) mit der Übersichtstabelle aller Pflanzen.
- **Lichtbedarf**: Einer der drei Werte: „Sonne", „Halbschatten" oder „Schatten".
- **Validator**: Die serverseitige Logik, die Formulareingaben prüft.
- **App**: Die Flask-Webanwendung (Garten-Tracker).
- **Browser**: Der Client, mit dem der Nutzer auf die App zugreift.
- **Mobilgerät**: Ein Gerät mit einer Bildschirmbreite von weniger als 600 px.

---

## Anforderungen

### Anforderung 1: Bearbeiten-Link in der Pflanzenliste

**User Story:** Als Gärtner möchte ich bei jeder Pflanze in der Liste einen „Bearbeiten"-Link sehen, damit ich schnell zur Bearbeitungsseite dieser Pflanze navigieren kann.

#### Akzeptanzkriterien

1. THE App SHALL für jede Pflanze in der Pflanzenliste einen Link mit dem Text „Bearbeiten" rendern, der auf `/plant/<id>/edit` verweist.
2. WHEN der Nutzer auf „Bearbeiten" klickt, THE Browser SHALL die Bearbeitungsseite der jeweiligen Pflanze laden.

---

### Anforderung 2: Bearbeitungsseite anzeigen (GET)

**User Story:** Als Gärtner möchte ich die Detailseite einer Pflanze aufrufen können, damit ich alle aktuellen Daten sehe und bearbeiten kann.

#### Akzeptanzkriterien

1. WHEN ein GET-Request an `/plant/<id>/edit` gesendet wird, THE App SHALL die Bearbeitungsseite mit einem Formular rendern, das die aktuellen Werte der Pflanze (name, type, variety, lichtbedarf, kommentar) vorausgefüllt enthält.
2. WHEN ein GET-Request an `/plant/<id>/edit` für eine nicht existierende Pflanze gesendet wird, THE App SHALL einen HTTP-404-Fehler zurückgeben.
3. THE Bearbeitungsseite SHALL alle Ereignisse der Pflanze anzeigen, jeweils mit Ereignistyp, Startmonat und Endmonat in deutscher Monatsbezeichnung.
4. THE Bearbeitungsseite SHALL ein Formular zum Hinzufügen eines neuen Ereignisses enthalten (Ereignistyp, Startmonat, Endmonat).
5. THE Bearbeitungsseite SHALL für jedes vorhandene Ereignis eine Schaltfläche zum Entfernen anzeigen.

---

### Anforderung 3: Pflanze speichern (POST)

**User Story:** Als Gärtner möchte ich geänderte Pflanzendaten speichern können, damit meine Korrekturen dauerhaft übernommen werden.

#### Akzeptanzkriterien

1. WHEN ein POST-Request an `/plant/<id>/edit` mit gültigen Formulardaten gesendet wird, THE App SHALL die Pflanzendaten in der Datenbank aktualisieren und den Browser auf die Pflanzenliste (`/`) weiterleiten.
2. WHEN ein POST-Request an `/plant/<id>/edit` mit leerem name-Feld gesendet wird, THE Validator SHALL die Anfrage ablehnen und die Bearbeitungsseite mit der Fehlermeldung „Name und Typ dürfen nicht leer sein." und HTTP-Status 400 zurückgeben.
3. WHEN ein POST-Request an `/plant/<id>/edit` mit leerem type-Feld gesendet wird, THE Validator SHALL die Anfrage ablehnen und die Bearbeitungsseite mit der Fehlermeldung „Name und Typ dürfen nicht leer sein." und HTTP-Status 400 zurückgeben.
4. WHEN ein POST-Request an `/plant/<id>/edit` mit einem ungültigen lichtbedarf-Wert gesendet wird, THE Validator SHALL die Anfrage ablehnen und die Bearbeitungsseite mit der Fehlermeldung „Lichtbedarf muss Sonne, Halbschatten oder Schatten sein." und HTTP-Status 400 zurückgeben.
5. WHEN ein POST-Request an `/plant/<id>/edit` für eine nicht existierende Pflanze gesendet wird, THE App SHALL einen HTTP-404-Fehler zurückgeben.
6. THE Validator SHALL variety und kommentar als optionale Felder behandeln; leere Eingaben werden als NULL in der Datenbank gespeichert.

---

### Anforderung 4: Ereignisse auf der Bearbeitungsseite verwalten

**User Story:** Als Gärtner möchte ich Ereignisse direkt auf der Bearbeitungsseite hinzufügen und entfernen können, damit ich nicht zur Hauptliste zurückkehren muss.

#### Akzeptanzkriterien

1. WHEN ein POST-Request an `/plant/<id>/ereignis/add` mit gültigen Daten gesendet wird, THE App SHALL das Ereignis speichern und den Browser auf die Bearbeitungsseite (`/plant/<id>/edit`) der jeweiligen Pflanze weiterleiten.
2. WHEN ein POST-Request an `/ereignis/<ereignis_id>/remove` von der Bearbeitungsseite aus gesendet wird, THE App SHALL das Ereignis löschen und den Browser auf die Bearbeitungsseite der zugehörigen Pflanze weiterleiten.
3. IF der Startmonat größer als der Endmonat ist, THEN THE Validator SHALL die Anfrage ablehnen und die Bearbeitungsseite mit der Fehlermeldung „Startmonat darf nicht größer als Endmonat sein." und HTTP-Status 400 zurückgeben.
4. IF ein ungültiger Ereignistyp übermittelt wird, THEN THE Validator SHALL die Anfrage ablehnen und die Bearbeitungsseite mit der Fehlermeldung „Ereignistyp ungültig." und HTTP-Status 400 zurückgeben.

---

### Anforderung 5: Kompakte Pflanzenliste auf Mobilgeräten

**User Story:** Als Gärtner möchte ich die Pflanzenliste auf meinem Smartphone übersichtlich sehen, damit ich schnell den Überblick behalte ohne horizontal scrollen zu müssen.

#### Akzeptanzkriterien

1. WHILE die Bildschirmbreite weniger als 600 px beträgt, THE App SHALL in der Pflanzenliste pro Pflanze nur Name, Typ und Lichtbedarf anzeigen.
2. WHILE die Bildschirmbreite weniger als 600 px beträgt, THE App SHALL die Spalten Sorte, Kommentar, Ereignisse und „Ereignis hinzufügen" in der Pflanzenliste ausblenden.
3. WHILE die Bildschirmbreite weniger als 600 px beträgt, THE App SHALL die Tabelle der Pflanzenliste als Kartenlayout (card layout) darstellen, bei dem jede Pflanze als eigenständige Karte erscheint.
4. THE App SHALL das viewport-Meta-Tag (`<meta name="viewport" content="width=device-width, initial-scale=1">`) in `base.html` enthalten.

---

### Anforderung 6: Touch-freundliche Bedienelemente

**User Story:** Als Gärtner möchte ich Schaltflächen und Formularelemente bequem mit dem Finger bedienen können, damit die App auf dem Smartphone gut nutzbar ist.

#### Akzeptanzkriterien

1. THE App SHALL alle interaktiven Elemente (Schaltflächen, Links, Select-Felder, Texteingaben) mit einer minimalen Touch-Zielfläche von 44 × 44 px auf Mobilgeräten rendern.
2. WHILE die Bildschirmbreite weniger als 600 px beträgt, THE App SHALL Formularfelder auf der Bearbeitungsseite mit einer Breite von 100 % des verfügbaren Bereichs darstellen.
3. THE App SHALL die responsive Darstellung ausschließlich durch CSS-Medienabfragen (media queries) ohne JavaScript-Frameworks umsetzen.
