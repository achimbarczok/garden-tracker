# Anforderungsdokument: Pflanzen-Fotos

## Einleitung

Diese Funktion ermöglicht es, pro Pflanze eine kleine Anzahl von Fotos hochzuladen und anzuzeigen. Die Fotos sind der Pflanze direkt zugeordnet (nicht einzelnen Ereignissen oder Beobachtungen) und dokumentieren die wenigen relevanten Zustände einer Pflanze (z.B. Blüte, Frucht, Habitus). Da die Anwendung auf einem Raspberry Pi läuft, werden hochgeladene Bilder serverseitig auf maximal 640 Pixel lange Seite verkleinert, um Speicherplatz und Ladezeiten gering zu halten. Die Bildverarbeitung erfolgt mit Pillow (PIL), das auf dem Raspberry Pi problemlos läuft.

## Glossar

- **Pflanze**: Ein Eintrag in der `plants`-Tabelle mit allen Stammdaten
- **Foto**: Eine Bilddatei (JPEG oder PNG), die einer Pflanze zugeordnet ist
- **Foto_Service**: Die serverseitige Logik in `db.py` und `app.py`, die Fotos speichert, verkleinert, abruft und löscht
- **Foto_Verzeichnis**: Das Verzeichnis auf dem Dateisystem, in dem die verkleinerten Fotos gespeichert werden (unterhalb des Docker-Volumes)
- **Bearbeitungsseite**: Die bestehende Seite unter `/plant/<id>/edit` (Template `edit.html`)
- **Pflanzenliste**: Die Hauptseite unter `/` (Template `index.html`)
- **Zustandsbezeichnung**: Ein optionaler Freitext-Label für ein Foto (z.B. „Blüte", „Frucht", „Habitus")
- **Hauptbild**: Das als primäres Vorschaubild markierte Foto einer Pflanze; pro Pflanze kann genau ein Foto als Hauptbild gesetzt sein
- **Lange_Seite**: Die längere der beiden Dimensionen (Breite oder Höhe) eines Bildes

## Anforderungen

### Anforderung 1: Foto hochladen

**User Story:** Als Gärtner möchte ich auf der Bearbeitungsseite einer Pflanze ein Foto hochladen können, damit ich den Zustand meiner Pflanze visuell dokumentieren kann.

#### Akzeptanzkriterien

1. THE Bearbeitungsseite SHALL ein Formular zum Hochladen eines Fotos für die aktuell angezeigte Pflanze anzeigen.
2. WHEN der Benutzer ein Foto hochlädt, THE Foto_Service SHALL die Datei entgegennehmen und der Pflanze zuordnen.
3. WHEN der Benutzer ein Foto hochlädt, THE Bearbeitungsseite SHALL ein optionales Freitext-Feld für die Zustandsbezeichnung anbieten (z.B. „Blüte", „Frucht").
4. WHEN das Foto erfolgreich gespeichert wurde, THE Anwendung SHALL den Benutzer zurück zur Bearbeitungsseite der Pflanze weiterleiten.

### Anforderung 2: Bildverkleinerung

**User Story:** Als Gärtner möchte ich, dass hochgeladene Fotos automatisch verkleinert werden, damit die Bilder auf dem Raspberry Pi wenig Speicherplatz benötigen.

#### Akzeptanzkriterien

1. WHEN ein Foto hochgeladen wird und die Lange_Seite des Bildes 640 Pixel überschreitet, THE Foto_Service SHALL das Bild proportional so verkleinern, dass die Lange_Seite exakt 640 Pixel beträgt.
2. WHEN ein Foto hochgeladen wird und die Lange_Seite des Bildes 640 Pixel oder weniger beträgt, THE Foto_Service SHALL das Bild in seiner Originalgröße belassen.
3. THE Foto_Service SHALL das verkleinerte Bild im JPEG-Format mit einer Qualitätsstufe von 85 speichern.
4. THE Foto_Service SHALL EXIF-Rotationsdaten beim Verkleinern berücksichtigen, damit Fotos von Smartphones korrekt orientiert gespeichert werden.

### Anforderung 3: Maximale Fotoanzahl pro Pflanze

**User Story:** Als Gärtner möchte ich, dass die Anzahl der Fotos pro Pflanze begrenzt ist, damit der Speicherverbrauch überschaubar bleibt.

#### Akzeptanzkriterien

1. THE Foto_Service SHALL maximal 5 Fotos pro Pflanze zulassen.
2. WHILE eine Pflanze bereits 5 Fotos besitzt, THE Bearbeitungsseite SHALL das Upload-Formular ausblenden und einen Hinweis anzeigen, dass das Maximum erreicht ist.
3. IF ein Upload-Versuch die maximale Fotoanzahl überschreiten würde, THEN THE Foto_Service SHALL den Upload ablehnen und eine Fehlermeldung zurückgeben.

### Anforderung 4: Fotos anzeigen

**User Story:** Als Gärtner möchte ich die Fotos einer Pflanze auf der Bearbeitungsseite sehen, damit ich einen visuellen Überblick über die dokumentierten Zustände habe.

#### Akzeptanzkriterien

1. THE Bearbeitungsseite SHALL alle Fotos der aktuell angezeigten Pflanze als Vorschaubilder (Thumbnails) anzeigen.
2. WHEN ein Foto eine Zustandsbezeichnung besitzt, THE Bearbeitungsseite SHALL die Zustandsbezeichnung unterhalb des Vorschaubildes anzeigen.
3. THE Anwendung SHALL die Fotos über eine statische Route ausliefern, die auf das Foto_Verzeichnis verweist.

### Anforderung 5: Foto löschen

**User Story:** Als Gärtner möchte ich ein Foto einer Pflanze löschen können, damit ich veraltete oder fehlerhafte Bilder entfernen kann.

#### Akzeptanzkriterien

1. THE Bearbeitungsseite SHALL neben jedem Foto einen Löschen-Button anzeigen.
2. WHEN der Benutzer den Löschen-Button betätigt, THE Foto_Service SHALL das Foto aus der Datenbank und vom Dateisystem entfernen.
3. WHEN das Foto erfolgreich gelöscht wurde, THE Anwendung SHALL den Benutzer zurück zur Bearbeitungsseite der Pflanze weiterleiten.

### Anforderung 6: Dateispeicherung

**User Story:** Als Gärtner möchte ich, dass die Fotos persistent im Docker-Volume gespeichert werden, damit sie bei Container-Neustarts erhalten bleiben.

#### Akzeptanzkriterien

1. THE Foto_Service SHALL die Fotodateien in einem Unterverzeichnis `fotos/` innerhalb des Docker-Volume-Pfades speichern (neben der SQLite-Datenbank).
2. THE Foto_Service SHALL jeden Dateinamen eindeutig generieren, um Namenskollisionen zu vermeiden.
3. THE Foto_Service SHALL die Foto-Metadaten (Dateiname, Pflanzen-ID, Zustandsbezeichnung) in einer neuen SQLite-Tabelle `fotos` speichern.
4. WHEN eine Pflanze gelöscht wird, THE Foto_Service SHALL alle zugehörigen Fotos sowohl aus der Datenbank als auch vom Dateisystem entfernen.

### Anforderung 7: Validierung des Uploads

**User Story:** Als Gärtner möchte ich, dass nur gültige Bilddateien akzeptiert werden, damit keine fehlerhaften Dateien gespeichert werden.

#### Akzeptanzkriterien

1. THE Foto_Service SHALL ausschließlich Dateien mit den MIME-Typen `image/jpeg` und `image/png` akzeptieren.
2. IF eine hochgeladene Datei einen ungültigen MIME-Typ besitzt, THEN THE Foto_Service SHALL den Upload ablehnen und die Fehlermeldung „Nur JPEG- und PNG-Dateien sind erlaubt." zurückgeben.
3. IF keine Datei ausgewählt wurde, THEN THE Foto_Service SHALL den Upload ablehnen und die Fehlermeldung „Bitte eine Bilddatei auswählen." zurückgeben.
4. THE Foto_Service SHALL die maximale Dateigröße vor der Verkleinerung auf 10 MB begrenzen.
5. IF eine hochgeladene Datei 10 MB überschreitet, THEN THE Foto_Service SHALL den Upload ablehnen und die Fehlermeldung „Die Datei ist zu groß (maximal 10 MB)." zurückgeben.

### Anforderung 8: Datenbankschema

**User Story:** Als Entwickler möchte ich, dass die Foto-Metadaten in einer eigenen Tabelle gespeichert werden, damit die Datenstruktur sauber bleibt.

#### Akzeptanzkriterien

1. THE Foto_Service SHALL eine Tabelle `fotos` mit den Spalten `id` (INTEGER PRIMARY KEY), `plant_id` (INTEGER, Fremdschlüssel auf `plants.id` mit ON DELETE CASCADE), `dateiname` (TEXT), `bezeichnung` (TEXT, optional) und `ist_hauptbild` (INTEGER DEFAULT 0) anlegen.
2. WHEN die Anwendung startet, THE Foto_Service SHALL die Tabelle `fotos` im Rahmen der bestehenden Schema-Migration erstellen, falls sie noch nicht existiert.

### Anforderung 9: Pillow-Abhängigkeit

**User Story:** Als Entwickler möchte ich, dass Pillow als Abhängigkeit hinzugefügt wird, damit die Bildverkleinerung funktioniert.

#### Akzeptanzkriterien

1. THE Anwendung SHALL `Pillow` in der Datei `requirements.txt` als Abhängigkeit aufführen.
2. THE Dockerfile SHALL `Pillow` ohne zusätzliche Systempakete installieren können (das Paket `python:3.12-slim` enthält die nötigen Bibliotheken für JPEG/PNG).

### Anforderung 10: Fehlerbehandlung

**User Story:** Als Gärtner möchte ich verständliche Fehlermeldungen erhalten, wenn beim Foto-Upload etwas schiefgeht.

#### Akzeptanzkriterien

1. IF die Pflanze nicht existiert, THEN THE Anwendung SHALL einen HTTP-404-Fehler zurückgeben.
2. IF ein Dateisystemfehler beim Speichern auftritt, THEN THE Foto_Service SHALL keine teilweisen Daten in der Datenbank hinterlassen.
3. IF ein Fehler beim Verkleinern des Bildes auftritt (z.B. beschädigte Datei), THEN THE Foto_Service SHALL den Upload ablehnen und die Fehlermeldung „Das Bild konnte nicht verarbeitet werden." zurückgeben.

### Anforderung 11: Hauptbild festlegen

**User Story:** Als Gärtner möchte ich ein Foto als Hauptbild einer Pflanze markieren können, damit dieses Bild später in Übersichten als repräsentatives Vorschaubild verwendet werden kann.

#### Akzeptanzkriterien

1. THE Foto_Service SHALL pro Pflanze genau ein Foto als Hauptbild zulassen.
2. WHEN das erste Foto einer Pflanze hochgeladen wird, THE Foto_Service SHALL dieses Foto automatisch als Hauptbild setzen.
3. WHEN der Benutzer ein anderes Foto als Hauptbild auswählt, THE Foto_Service SHALL das bisherige Hauptbild zurücksetzen und das neu gewählte Foto als Hauptbild markieren.
4. THE Bearbeitungsseite SHALL neben jedem Foto einen Button zum Setzen als Hauptbild anzeigen.
5. THE Bearbeitungsseite SHALL das aktuelle Hauptbild visuell hervorheben (z.B. durch einen Rahmen oder ein Stern-Symbol).
6. WHEN das aktuelle Hauptbild gelöscht wird und weitere Fotos vorhanden sind, THE Foto_Service SHALL kein anderes Foto automatisch als Hauptbild setzen; der Benutzer wählt manuell ein neues Hauptbild.
7. THE Foto_Service SHALL den Hauptbild-Status über eine boolesche Spalte `ist_hauptbild` in der Tabelle `fotos` speichern.
