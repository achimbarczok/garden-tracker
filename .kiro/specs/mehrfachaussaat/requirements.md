# Anforderungsdokument: Mehrfachaussaat

## Einleitung

Viele Gemüsepflanzen (z. B. Zuckererbsen, Radieschen, Salat) haben einen Aussaatzeitraum, in dem man sie mehrfach säen kann, um versetzt zu ernten. Das aktuelle Datenmodell kennt pro Pflanze nur einen Satz erwarteter Ereignisse (Blüte, Ernte, etc.). Diese Erweiterung führt das Konzept **Satz** (= eine einzelne Aussaat/Pflanzung) ein: Jede Pflanze kann mehrere Sätze haben, und jeder Satz hat eigene erwartete Ereignisse mit individuellen Zeitfenstern.

Damit kann der Nutzer z. B. Zuckererbsen im März und nochmal im April säen und für jeden Satz getrennt sehen, wann Blüte und Ernte zu erwarten sind.

## Glossar

- **Garden_App**: Die bestehende Webanwendung zur Gartenverwaltung.
- **Pflanze**: Ein erfasster Garteneintrag mit Name, Kategorie, Typ, Sorte und weiteren Stammdaten.
- **Satz**: Eine einzelne Aussaat oder Pflanzung einer Pflanze zu einem bestimmten Zeitpunkt. Eine Pflanze kann null oder mehrere Sätze haben.
- **Satz_Bezeichnung**: Ein vom Nutzer vergebener kurzer Name für einen Satz (z. B. „1. Aussaat März", „2. Aussaat April").
- **Satz_Aussaatdatum**: Der Monat (und optional Anfang/Mitte/Ende), in dem der Satz ausgesät oder gepflanzt wurde.
- **Satz_Ereignis**: Ein erwartetes Ereignis, das einem bestimmten Satz zugeordnet ist (z. B. Blüte Mai–Juni für den 1. Satz).
- **Satz_Beobachtung**: Eine tatsächliche Beobachtung, die einem bestimmten Satz zugeordnet ist.
- **Ereignis**: Ein erwartetes zeitliches Ereignis (Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat) mit Start- und Endmonat.
- **Beobachtung**: Eine tatsächlich beobachtete Ausprägung eines Ereignisses in einem bestimmten Jahr.
- **Monat**: Eine Ganzzahl von 1 (Januar) bis 12 (Dezember).
- **Detail**: Optionale Präzisierung innerhalb eines Monats: Anfang, Mitte oder Ende.
- **SQLite_Store**: Die SQLite-Datenbankdatei als primärer Datenspeicher.
- **Edit_Page**: Die Bearbeitungsseite einer einzelnen Pflanze (`/plant/<id>/edit`).

---

## Anforderungen

### Anforderung 1: Sätze pro Pflanze anlegen und verwalten

**User Story:** Als Gärtner möchte ich für eine Pflanze mehrere Sätze (Aussaaten/Pflanzungen) anlegen, damit ich versetzte Aussaaten getrennt verfolgen kann.

#### Akzeptanzkriterien

1. THE Garden_App SHALL allow associating zero or more Sätze with each Pflanze.
2. WHEN a user adds a Satz to a Pflanze, THE Garden_App SHALL record a Satz_Bezeichnung and a Satz_Aussaatdatum (Monat und optionales Detail).
3. WHEN a user adds a Satz without Satz_Bezeichnung, THE Garden_App SHALL reject the submission and display a German-language error message.
4. WHEN a user adds a Satz, THE Garden_App SHALL accept only Monat values between 1 and 12 (inclusive) for the Satz_Aussaatdatum.
5. THE Garden_App SHALL allow the user to edit the Satz_Bezeichnung and das Satz_Aussaatdatum eines bestehenden Satzes.
6. THE Garden_App SHALL allow the user to remove a Satz from a Pflanze.
7. WHEN a Satz is removed, THE Garden_App SHALL also remove all Satz_Ereignisse and Satz_Beobachtungen associated with that Satz.
8. WHEN a Pflanze is removed, THE Garden_App SHALL also remove all Sätze (and deren Satz_Ereignisse and Satz_Beobachtungen) associated with that Pflanze.

---

### Anforderung 2: Erwartete Ereignisse pro Satz

**User Story:** Als Gärtner möchte ich für jeden Satz eigene erwartete Ereignisse (Blüte, Ernte, etc.) mit individuellen Zeitfenstern erfassen, damit ich weiß, wann ich bei welcher Aussaat mit welchem Ereignis rechnen kann.

#### Akzeptanzkriterien

1. THE Garden_App SHALL allow associating zero or more Satz_Ereignisse with each Satz.
2. WHEN a user adds a Satz_Ereignis, THE Garden_App SHALL record den Ereignistyp, Startmonat, Endmonat und optionale Details (Anfang/Mitte/Ende).
3. WHEN a Satz_Ereignis is saved, THE Garden_App SHALL accept only the valid Ereignistypen (Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat).
4. WHEN a Satz_Ereignis is saved, THE Garden_App SHALL accept only Monat values between 1 and 12 (inclusive) for Startmonat and Endmonat.
5. IF the Startmonat of a Satz_Ereignis is greater than the Endmonat (bei Zeitraum-Ereignistypen), THEN THE Garden_App SHALL reject the submission and display a German-language error message.
6. THE Garden_App SHALL allow the user to edit and remove individual Satz_Ereignisse.

---

### Anforderung 3: Beobachtungen pro Satz

**User Story:** Als Gärtner möchte ich Beobachtungen einem bestimmten Satz zuordnen können, damit ich die tatsächlichen Ergebnisse jeder Aussaat getrennt dokumentiere.

#### Akzeptanzkriterien

1. THE Garden_App SHALL allow associating zero or more Satz_Beobachtungen with each Satz.
2. WHEN a user adds a Satz_Beobachtung, THE Garden_App SHALL record Jahr, Ereignistyp, Startmonat, Endmonat, optionale Details und optionale Notiz.
3. THE Garden_App SHALL allow the user to edit and remove individual Satz_Beobachtungen.

---

### Anforderung 4: Darstellung der Sätze auf der Edit-Seite

**User Story:** Als Gärtner möchte ich auf der Bearbeitungsseite einer Pflanze alle Sätze mit ihren jeweiligen Ereignissen und Beobachtungen übersichtlich sehen, damit ich den Überblick über meine versetzten Aussaaten behalte.

#### Akzeptanzkriterien

1. WHEN the Edit_Page is rendered for a Pflanze with Sätzen, THE Garden_App SHALL display each Satz with seiner Satz_Bezeichnung and dem Satz_Aussaatdatum.
2. WHEN the Edit_Page is rendered, THE Garden_App SHALL display die Satz_Ereignisse and Satz_Beobachtungen innerhalb des jeweiligen Satzes gruppiert.
3. WHEN a Pflanze has no Sätze, THE Garden_App SHALL display a message indicating that no Sätze exist and offer a form to add one.
4. THE Garden_App SHALL provide a form within each Satz section to add Satz_Ereignisse and Satz_Beobachtungen.
5. THE Garden_App SHALL provide a form on the Edit_Page to add a new Satz.

---

### Anforderung 5: Darstellung der Sätze in der Pflanzenliste

**User Story:** Als Gärtner möchte ich in der Pflanzenliste auf einen Blick sehen, wie viele Sätze eine Pflanze hat, damit ich schnell erkenne, welche Pflanzen mehrfach ausgesät wurden.

#### Akzeptanzkriterien

1. WHEN the Plant_List is rendered for a Pflanze with Sätzen, THE Garden_App SHALL display the number of Sätze next to the plant name.
2. WHEN a Pflanze has no Sätze, THE Garden_App SHALL display the existing Ereignisse of the Pflanze as before (without Satz-Hinweis).

---

### Anforderung 6: Koexistenz mit bestehenden Ereignissen und Beobachtungen

**User Story:** Als Gärtner möchte ich, dass meine bestehenden Ereignisse und Beobachtungen (ohne Satz-Zuordnung) weiterhin funktionieren, damit ich nicht gezwungen bin, sofort alles auf Sätze umzustellen.

#### Akzeptanzkriterien

1. THE Garden_App SHALL continue to support Ereignisse and Beobachtungen that are not associated with any Satz (pflanzweite Ereignisse).
2. WHEN the Edit_Page is rendered, THE Garden_App SHALL display pflanzweite Ereignisse and Beobachtungen in einem separaten Bereich oberhalb der Sätze.
3. WHEN a user adds an Ereignis or Beobachtung without Satz-Zuordnung, THE Garden_App SHALL store the entry as pflanzweites Ereignis (wie bisher).

---

### Anforderung 7: Datenmigration und Abwärtskompatibilität

**User Story:** Als Betreiber möchte ich, dass bestehende Daten nach dem Update erhalten bleiben und die neue Satz-Funktionalität ohne Datenverlust verfügbar ist.

#### Akzeptanzkriterien

1. WHEN the Garden_App starts and the `saetze` table does not exist, THE Garden_App SHALL create it without affecting existing tables.
2. WHEN the Garden_App starts and the `satz_ereignisse` table does not exist, THE Garden_App SHALL create it without affecting existing tables.
3. WHEN the Garden_App starts and the `satz_beobachtungen` table does not exist, THE Garden_App SHALL create it without affecting existing tables.
4. WHEN existing Pflanze records are loaded after migration, THE Garden_App SHALL display them with their existing Ereignisse and Beobachtungen unchanged.
