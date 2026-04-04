# Anforderungsdokument: Phänologischer Kalender

## Einleitung

Erweiterung des Garten-Trackers um ein phänologisches Logbuch. Der Nutzer kann für jedes Jahr die 10 phänologischen Jahreszeiten mit ihren Zeiträumen erfassen. Auf der Startseite wird die aktuelle phänologische Phase angezeigt. Über die Jahre entsteht so ein Vergleichsarchiv.

## Glossar

- **Phänologische Phase**: Eine der 10 Jahreszeiten des phänologischen Kalenders (Vorfrühling bis Winter).
- **Phaenologie-Eintrag**: Ein Datensatz mit Jahr, Phase, Startmonat (mit optionalem Detail) und Endmonat (mit optionalem Detail).
- **Detail**: Optionale Präzisierung eines Monats: Anfang, Mitte oder Ende.

## Anforderungen

### Anforderung 1: Phänologische Phasen pro Jahr erfassen

**User Story:** Als Gärtner möchte ich für jedes Jahr die phänologischen Phasen mit ihren Zeiträumen eintragen, damit ich ein Logbuch meiner lokalen Jahreszeiten aufbaue.

#### Akzeptanzkriterien

1. THE App SHALL eine eigene Seite `/phaenologie` bereitstellen.
2. THE App SHALL die 10 festen phänologischen Phasen unterstützen: Vorfrühling, Erstfrühling, Vollfrühling, Frühsommer, Hochsommer, Spätsommer, Frühherbst, Vollherbst, Spätherbst, Winter.
3. WHEN ein Nutzer eine Phase für ein Jahr einträgt, THE App SHALL Startmonat, optionales Start-Detail, Endmonat und optionales End-Detail speichern.
4. WHEN eine Phase für ein Jahr bereits existiert, THE App SHALL den bestehenden Eintrag aktualisieren (Upsert).
5. THE App SHALL pro Jahr und Phase maximal einen Eintrag erlauben (UNIQUE-Constraint).
6. WHEN ein Nutzer einen Phasen-Eintrag entfernt, THE App SHALL ihn aus der Datenbank löschen.

---

### Anforderung 2: Jahresübersicht und Vergleich

**User Story:** Als Gärtner möchte ich die Phasen verschiedener Jahre vergleichen können, damit ich Trends und Abweichungen erkenne.

#### Akzeptanzkriterien

1. THE App SHALL auf der Phänologie-Seite eine Jahresauswahl per Dropdown anbieten.
2. WHEN ein Jahr ausgewählt wird, THE App SHALL alle eingetragenen Phasen für dieses Jahr als Tabelle anzeigen.
3. THE App SHALL alle Jahre mit Phänologie-Daten im Dropdown auflisten.
4. THE App SHALL das aktuelle Jahr immer im Dropdown anzeigen, auch wenn noch keine Daten vorhanden sind.

---

### Anforderung 3: Aktuelle Phase auf der Startseite

**User Story:** Als Gärtner möchte ich auf der Startseite sofort sehen, in welcher phänologischen Jahreszeit wir uns befinden.

#### Akzeptanzkriterien

1. WHEN Phänologie-Daten für das aktuelle Jahr vorhanden sind, THE App SHALL die aktuelle Phase auf der Startseite anzeigen.
2. THE App SHALL die aktuelle Phase bestimmen, indem sie das heutige Datum mit den Zeiträumen der eingetragenen Phasen abgleicht.
3. WHEN keine Phänologie-Daten für das aktuelle Jahr vorhanden sind, THE App SHALL einen Hinweis mit Link zur Phänologie-Seite anzeigen.
4. THE App SHALL Detail-Werte in ungefähre Tage umrechnen: Anfang ≈ 5., Mitte ≈ 15., Ende ≈ 25., kein Detail ≈ 1.

---

### Anforderung 4: Navigation

**User Story:** Als Nutzer möchte ich die Phänologie-Seite einfach erreichen können.

#### Akzeptanzkriterien

1. THE App SHALL einen Link zur Phänologie-Seite im Header anzeigen.
2. THE App SHALL auf der Phänologie-Seite einen Zurück-Link zur Startseite anzeigen.
