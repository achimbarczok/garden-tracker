# Anforderungsdokument: Pflanzenereignisse

## Einleitung

Diese Erweiterung des Garden Trackers fügt drei neue Felder zur Pflanzenverwaltung hinzu:

1. **Ereignisse** — Zeitlich begrenzte Ereignisse pro Pflanze (z. B. Blüte, Ernte, Düngen, Rückschnitt), jeweils mit einem Startmonat und einem Endmonat.
2. **Lichtbedarf** — Ein Pflichtfeld mit drei festen Optionen: Sonne, Halbschatten, Schatten.
3. **Kommentar** — Ein optionales Freitextfeld für Notizen und besondere Eigenschaften der Pflanze.

Die Erweiterung baut auf dem bestehenden Flask + SQLite + Jinja2-Stack auf. Die Benutzeroberfläche bleibt vollständig auf Deutsch.

---

## Glossar

- **Garden_App**: Die bestehende Webanwendung zur Gartenverwaltung.
- **Plant**: Ein erfasster Garteneintrag mit Name, Typ, optionaler Sorte sowie den neuen Feldern Lichtbedarf, Kommentar und Ereignissen.
- **Ereignis**: Ein zeitlich begrenztes Ereignis einer Pflanze mit einem Ereignistyp, einem Startmonat und einem Endmonat.
- **Ereignistyp**: Eine der vier festen Kategorien: Blüte, Ernte, Düngen, Rückschnitt.
- **Lichtbedarf**: Die Lichtanforderung einer Pflanze — eine der drei Optionen: Sonne, Halbschatten, Schatten.
- **Kommentar**: Ein optionaler Freitext mit Notizen oder besonderen Eigenschaften einer Pflanze.
- **Monat**: Eine Ganzzahl von 1 (Januar) bis 12 (Dezember).
- **SQLite_Store**: Die SQLite-Datenbankdatei als primärer Datenspeicher.
- **Plant_List**: Die Ansicht, die alle erfassten Pflanzen mit ihren Informationen anzeigt.

---

## Anforderungen

### Anforderung 1: Ereignisse pro Pflanze

**User Story:** Als Gärtner möchte ich für jede Pflanze mehrere Ereignisse mit Zeitfenstern erfassen, damit ich auf einen Blick sehe, wann Blüte, Ernte, Düngen oder Rückschnitt anstehen.

#### Akzeptanzkriterien

1. THE Garden_App SHALL allow associating zero or more Ereignisse with each Plant.
2. WHEN a user adds an Ereignis to a Plant, THE Garden_App SHALL record the Ereignistyp, the Startmonat, and the Endmonat.
3. WHEN an Ereignis is saved, THE Garden_App SHALL accept only the Ereignistypen: Blüte, Ernte, Düngen, Rückschnitt.
4. WHEN an Ereignis is saved, THE Garden_App SHALL accept only Monat values between 1 and 12 (inclusive) for both Startmonat and Endmonat.
5. IF the Startmonat of an Ereignis is greater than the Endmonat, THEN THE Garden_App SHALL reject the Ereignis and display a German-language error message.
6. THE Garden_App SHALL support multiple Ereignisse of different Ereignistypen for the same Plant.
7. THE Garden_App SHALL support multiple Ereignisse of the same Ereignistyp for the same Plant.
8. WHEN a Plant is removed, THE Garden_App SHALL also remove all Ereignisse associated with that Plant.

---

### Anforderung 2: Ereignisse in der Pflanzenliste anzeigen

**User Story:** Als Gärtner möchte ich die Ereignisse jeder Pflanze direkt in der Pflanzenliste sehen, damit ich keine separate Detailansicht öffnen muss.

#### Akzeptanzkriterien

1. WHEN the Plant_List is rendered, THE Garden_App SHALL display all Ereignisse for each Plant alongside the plant's other fields.
2. WHEN the Plant_List is rendered, THE Garden_App SHALL display each Ereignis with its Ereignistyp, Startmonat, and Endmonat.
3. WHEN a Plant has no Ereignisse, THE Garden_App SHALL display the plant row without an Ereignis section (no placeholder text required).

---

### Anforderung 3: Lichtbedarf der Pflanze

**User Story:** Als Gärtner möchte ich den Lichtbedarf jeder Pflanze erfassen, damit ich beim Einpflanzen den richtigen Standort wählen kann.

#### Akzeptanzkriterien

1. WHEN a user adds a Plant, THE Garden_App SHALL require the user to select a Lichtbedarf value.
2. THE Garden_App SHALL accept only the Lichtbedarf values: Sonne, Halbschatten, Schatten.
3. IF a user submits the add-plant form without selecting a Lichtbedarf, THEN THE Garden_App SHALL reject the submission and display a German-language error message.
4. WHEN the Plant_List is rendered, THE Garden_App SHALL display the Lichtbedarf for each Plant.

---

### Anforderung 4: Kommentar zur Pflanze

**User Story:** Als Gärtner möchte ich einen freien Kommentar zu jeder Pflanze hinterlegen, damit ich besondere Eigenschaften oder Pflegehinweise festhalten kann.

#### Akzeptanzkriterien

1. WHEN a user adds a Plant, THE Garden_App SHALL allow the user to optionally enter a Kommentar.
2. THE Garden_App SHALL store the Kommentar as free text without length restriction enforced by the application.
3. WHEN the Plant_List is rendered, THE Garden_App SHALL display the Kommentar for each Plant that has one.
4. WHEN a Plant has no Kommentar, THE Garden_App SHALL display the plant row without a Kommentar field.

---

### Anforderung 5: Datenmigration und Abwärtskompatibilität

**User Story:** Als Betreiber möchte ich, dass bestehende Pflanzendaten nach dem Update erhalten bleiben, damit ich keine Daten verliere.

#### Akzeptanzkriterien

1. WHEN the Garden_App starts and the existing `plants` table lacks the `lichtbedarf` or `kommentar` columns, THE Garden_App SHALL add the missing columns without deleting existing rows.
2. WHEN the Garden_App starts and the `ereignisse` table does not exist, THE Garden_App SHALL create it without affecting the `plants` table.
3. WHEN existing Plant records are loaded after migration, THE Garden_App SHALL display them with an empty Kommentar and no Ereignisse, and SHALL treat the missing Lichtbedarf as an empty value requiring no forced default.
