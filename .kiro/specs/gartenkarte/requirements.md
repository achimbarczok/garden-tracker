# Anforderungsdokument: Gartenkarte

## Einleitung

Diese Funktion ermöglicht es, eine visuelle Karte des Gartens anzuzeigen, auf der Pflanzen frei positioniert werden können. Als Hintergrund dient ein vom Benutzer hochgeladenes Bild (Foto oder Skizze des Gartens von oben). Pflanzen aus der bestehenden Pflanzenliste können per Klick auf der Karte platziert werden, sodass der Benutzer auf einen Blick sieht, wo welche Pflanze im Garten steht. Die Karte wird serverseitig gerendert; die Positionierung erfolgt über minimales Inline-JavaScript (Klick-Koordinaten erfassen), ohne externe JS-Frameworks.

## Glossar

- **Pflanze**: Ein Eintrag in der `plants`-Tabelle mit allen Stammdaten
- **Gartenkarte**: Die Seite unter `/gartenkarte`, die das Kartenbild mit platzierten Pflanzen anzeigt
- **Kartenbild**: Ein vom Benutzer hochgeladenes Hintergrundbild (Foto oder Skizze des Gartens von oben)
- **Kartenbild_Service**: Die serverseitige Logik in `db.py` und `app.py`, die das Kartenbild speichert, verkleinert, abruft und löscht
- **Kartenposition**: Ein Datensatz, der eine Pflanze mit einer relativen X/Y-Position (in Prozent) auf dem Kartenbild verknüpft
- **Positionierungs_Service**: Die serverseitige Logik in `db.py` und `app.py`, die Kartenpositionen erstellt, aktualisiert und löscht
- **Relative_Koordinaten**: X- und Y-Werte als Prozentwerte (0.0 bis 100.0) relativ zur Bildgröße, damit die Positionen bei unterschiedlichen Bildschirmgrößen korrekt skalieren
- **Kartenverzeichnis**: Das Verzeichnis auf dem Dateisystem, in dem das Kartenbild gespeichert wird (unterhalb des Docker-Volumes)

## Anforderungen

### Anforderung 1: Kartenbild hochladen

**User Story:** Als Gärtner möchte ich ein Bild meines Gartens (Foto oder Skizze von oben) hochladen können, damit dieses als Hintergrund für die Gartenkarte dient.

#### Akzeptanzkriterien

1. THE Gartenkarte SHALL ein Formular zum Hochladen eines Kartenbildes anzeigen, solange kein Kartenbild vorhanden ist.
2. WHEN der Benutzer ein Kartenbild hochlädt, THE Kartenbild_Service SHALL die Datei entgegennehmen und im Kartenverzeichnis speichern.
3. WHEN das Kartenbild erfolgreich gespeichert wurde, THE Anwendung SHALL den Benutzer zurück zur Gartenkarte weiterleiten.
4. THE Kartenbild_Service SHALL ausschließlich Dateien mit den MIME-Typen `image/jpeg` und `image/png` akzeptieren.
5. IF eine hochgeladene Datei einen ungültigen MIME-Typ besitzt, THEN THE Kartenbild_Service SHALL den Upload ablehnen und die Fehlermeldung „Nur JPEG- und PNG-Dateien sind erlaubt." zurückgeben.
6. IF keine Datei ausgewählt wurde, THEN THE Kartenbild_Service SHALL den Upload ablehnen und die Fehlermeldung „Bitte eine Bilddatei auswählen." zurückgeben.
7. THE Kartenbild_Service SHALL die maximale Dateigröße auf 10 MB begrenzen.

### Anforderung 2: Bildverkleinerung des Kartenbildes

**User Story:** Als Gärtner möchte ich, dass das hochgeladene Kartenbild automatisch auf eine sinnvolle Größe verkleinert wird, damit es auf dem Raspberry Pi wenig Speicherplatz benötigt und schnell lädt.

#### Akzeptanzkriterien

1. WHEN ein Kartenbild hochgeladen wird und die lange Seite des Bildes 1920 Pixel überschreitet, THE Kartenbild_Service SHALL das Bild proportional so verkleinern, dass die lange Seite 1920 Pixel beträgt.
2. WHEN ein Kartenbild hochgeladen wird und die lange Seite des Bildes 1920 Pixel oder weniger beträgt, THE Kartenbild_Service SHALL das Bild in seiner Originalgröße belassen.
3. THE Kartenbild_Service SHALL das verkleinerte Bild im JPEG-Format mit einer Qualitätsstufe von 85 speichern.
4. THE Kartenbild_Service SHALL EXIF-Rotationsdaten beim Verkleinern berücksichtigen, damit Fotos von Smartphones korrekt orientiert gespeichert werden.

### Anforderung 3: Kartenbild ersetzen und löschen

**User Story:** Als Gärtner möchte ich das Kartenbild austauschen oder löschen können, damit ich die Karte aktualisieren kann, wenn sich der Garten verändert.

#### Akzeptanzkriterien

1. WHILE ein Kartenbild vorhanden ist, THE Gartenkarte SHALL einen Button zum Ersetzen des Kartenbildes anzeigen.
2. WHEN der Benutzer ein neues Kartenbild hochlädt, THE Kartenbild_Service SHALL das bisherige Kartenbild vom Dateisystem löschen und das neue Bild speichern.
3. WHILE ein Kartenbild vorhanden ist, THE Gartenkarte SHALL einen Button zum Löschen des Kartenbildes anzeigen.
4. WHEN der Benutzer das Kartenbild löscht, THE Kartenbild_Service SHALL das Bild vom Dateisystem und die Metadaten aus der Datenbank entfernen.
5. WHEN das Kartenbild gelöscht wird, THE Positionierungs_Service SHALL alle zugehörigen Kartenpositionen aus der Datenbank entfernen.

### Anforderung 4: Pflanze auf der Karte platzieren

**User Story:** Als Gärtner möchte ich eine Pflanze aus meiner Pflanzenliste auf der Karte platzieren können, damit ich sehe, wo sie im Garten steht.

#### Akzeptanzkriterien

1. WHILE ein Kartenbild vorhanden ist, THE Gartenkarte SHALL ein Auswahlfeld (Dropdown) mit allen aktiven Pflanzen anzeigen.
2. WHEN der Benutzer eine Pflanze im Dropdown auswählt und auf das Kartenbild klickt, THE Gartenkarte SHALL die Klick-Koordinaten als Relative_Koordinaten erfassen und per Formular an den Server senden.
3. WHEN der Server gültige Koordinaten und eine gültige Pflanzen-ID empfängt, THE Positionierungs_Service SHALL eine neue Kartenposition in der Datenbank speichern.
4. THE Positionierungs_Service SHALL die Koordinaten als Prozentwerte (0.0 bis 100.0) relativ zur Bildgröße speichern.
5. IF die Pflanzen-ID ungültig ist oder die Pflanze nicht existiert, THEN THE Positionierungs_Service SHALL die Anfrage ablehnen und einen HTTP-404-Fehler zurückgeben.
6. THE Positionierungs_Service SHALL erlauben, dass dieselbe Pflanze an mehreren Positionen auf der Karte platziert wird.

### Anforderung 5: Platzierte Pflanzen auf der Karte anzeigen

**User Story:** Als Gärtner möchte ich alle platzierten Pflanzen auf der Karte sehen, damit ich einen visuellen Überblick über meinen Garten habe.

#### Akzeptanzkriterien

1. WHILE ein Kartenbild vorhanden ist, THE Gartenkarte SHALL alle gespeicherten Kartenpositionen als Markierungen über dem Kartenbild anzeigen.
2. THE Gartenkarte SHALL jede Markierung an der gespeicherten Relative_Koordinaten-Position über dem Kartenbild positionieren (mittels CSS `position: absolute` und Prozentwerten).
3. THE Gartenkarte SHALL den Namen der Pflanze als Tooltip (HTML `title`-Attribut) an jeder Markierung anzeigen.
4. WHEN eine Pflanze eine Farbe (`farbe`-Feld) besitzt, THE Gartenkarte SHALL die Markierung in dieser Farbe darstellen.
5. WHEN eine Pflanze keine Farbe besitzt, THE Gartenkarte SHALL die Markierung in einer Standardfarbe darstellen.

### Anforderung 6: Kartenposition entfernen

**User Story:** Als Gärtner möchte ich eine platzierte Pflanze von der Karte entfernen können, damit die Karte aktuell bleibt, wenn ich Pflanzen umsetze oder entferne.

#### Akzeptanzkriterien

1. THE Gartenkarte SHALL neben jeder Markierung eine Möglichkeit zum Entfernen der Kartenposition anbieten.
2. WHEN der Benutzer eine Kartenposition entfernt, THE Positionierungs_Service SHALL den Datensatz aus der Datenbank löschen.
3. WHEN die Kartenposition erfolgreich entfernt wurde, THE Anwendung SHALL den Benutzer zurück zur Gartenkarte weiterleiten.
4. WHEN eine Pflanze aus der Pflanzenliste gelöscht wird, THE Positionierungs_Service SHALL alle zugehörigen Kartenpositionen automatisch entfernen (via ON DELETE CASCADE).

### Anforderung 7: Datenbankschema

**User Story:** Als Entwickler möchte ich, dass die Kartendaten in eigenen Tabellen gespeichert werden, damit die Datenstruktur sauber bleibt.

#### Akzeptanzkriterien

1. THE Positionierungs_Service SHALL eine Tabelle `kartenpositionen` mit den Spalten `id` (INTEGER PRIMARY KEY), `plant_id` (INTEGER, Fremdschlüssel auf `plants.id` mit ON DELETE CASCADE), `x` (REAL, Prozentwert 0.0–100.0) und `y` (REAL, Prozentwert 0.0–100.0) anlegen.
2. THE Kartenbild_Service SHALL eine Tabelle `kartenbild` mit den Spalten `id` (INTEGER PRIMARY KEY), `dateiname` (TEXT) anlegen.
3. THE Kartenbild_Service SHALL maximal einen Eintrag in der Tabelle `kartenbild` zulassen (es gibt genau ein Kartenbild oder keines).
4. WHEN die Anwendung startet, THE Anwendung SHALL die Tabellen `kartenbild` und `kartenpositionen` im Rahmen der bestehenden Schema-Migration erstellen, falls sie noch nicht existieren.

### Anforderung 8: Dateispeicherung des Kartenbildes

**User Story:** Als Gärtner möchte ich, dass das Kartenbild persistent im Docker-Volume gespeichert wird, damit es bei Container-Neustarts erhalten bleibt.

#### Akzeptanzkriterien

1. THE Kartenbild_Service SHALL die Kartenbild-Datei in einem Unterverzeichnis `karte/` innerhalb des Docker-Volume-Pfades speichern (neben der SQLite-Datenbank).
2. THE Kartenbild_Service SHALL den Dateinamen eindeutig generieren (UUID), um Namenskollisionen zu vermeiden.
3. WHEN ein neues Kartenbild hochgeladen wird und ein altes existiert, THE Kartenbild_Service SHALL die alte Datei vom Dateisystem löschen, bevor die neue gespeichert wird.

### Anforderung 9: Navigation

**User Story:** Als Gärtner möchte ich die Gartenkarte über die Navigation erreichen können, damit ich schnell zwischen Pflanzenliste und Karte wechseln kann.

#### Akzeptanzkriterien

1. THE Anwendung SHALL einen Navigationslink „🗺️ Karte" in der Kopfzeile (Header-Navigation) anzeigen.
2. WHEN der Benutzer den Navigationslink betätigt, THE Anwendung SHALL die Gartenkarte unter der Route `/gartenkarte` anzeigen.
3. WHILE der Benutzer sich auf der Gartenkarte befindet, THE Anwendung SHALL den Navigationslink als aktiv hervorheben.

### Anforderung 10: Responsives Layout

**User Story:** Als Gärtner möchte ich die Gartenkarte auch auf dem Smartphone nutzen können, damit ich im Garten nachschauen kann, wo welche Pflanze steht.

#### Akzeptanzkriterien

1. THE Gartenkarte SHALL das Kartenbild so skalieren, dass es die volle verfügbare Breite des Bildschirms nutzt und das Seitenverhältnis beibehalten wird.
2. THE Gartenkarte SHALL die Markierungen bei jeder Bildschirmgröße korrekt über dem Kartenbild positionieren (durch Verwendung von Prozentwerten).
3. THE Gartenkarte SHALL auf Bildschirmen unter 600 Pixel Breite die Steuerelemente (Dropdown, Buttons) unterhalb des Kartenbildes anzeigen.

### Anforderung 11: Fehlerbehandlung

**User Story:** Als Gärtner möchte ich verständliche Fehlermeldungen erhalten, wenn beim Kartenbild-Upload oder bei der Positionierung etwas schiefgeht.

#### Akzeptanzkriterien

1. IF ein Dateisystemfehler beim Speichern des Kartenbildes auftritt, THEN THE Kartenbild_Service SHALL keine teilweisen Daten in der Datenbank hinterlassen.
2. IF ein Fehler beim Verkleinern des Kartenbildes auftritt (z.B. beschädigte Datei), THEN THE Kartenbild_Service SHALL den Upload ablehnen und die Fehlermeldung „Das Bild konnte nicht verarbeitet werden." zurückgeben.
3. IF die übermittelten Koordinaten außerhalb des gültigen Bereichs (0.0–100.0) liegen, THEN THE Positionierungs_Service SHALL die Anfrage ablehnen und die Fehlermeldung „Ungültige Koordinaten." zurückgeben.
4. IF kein Kartenbild vorhanden ist und der Benutzer versucht eine Pflanze zu platzieren, THEN THE Positionierungs_Service SHALL die Anfrage ablehnen und die Fehlermeldung „Bitte zuerst ein Kartenbild hochladen." zurückgeben.
