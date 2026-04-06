# Anforderungsdokument: UI-Konsistenz-Verbesserungen

## Einleitung

Drei zusammenhängende Verbesserungen der Benutzeroberfläche des Garten-Trackers, um ein einheitliches Erscheinungsbild und konsistente Navigation über alle Seiten hinweg sicherzustellen. Konkret: (1) Pflanzennamen mit Farbkreis auf Tagebuch- und Jahresplan-Seite wie auf der Startseite, (2) Klick auf Pflanzennamen auf der Startseite führt zur Detailseite, (3) Ereignisse direkt über die Tagebuchseite eintragen.

## Glossar

- **Startseite**: Die Hauptseite (`index.html`) mit der Pflanzenliste unter `/`
- **Tagebuchseite**: Die seitenübergreifende Beobachtungsliste (`beobachtungen.html`) unter `/beobachtungen`
- **Jahresplanseite**: Die seitenübergreifende Ereignisliste (`ereignisse.html`) unter `/ereignisse`
- **Detailseite**: Die Bearbeitungsseite einer einzelnen Pflanze (`edit.html`) unter `/plant/<id>/edit`
- **Farbkreis**: Ein farbiger Punkt (CSS-Klasse `color-dot`), der die individuell zugewiesene Farbe einer Pflanze anzeigt
- **Pflanzenliste**: Die tabellarische Darstellung aller Pflanzen auf der Startseite
- **Beobachtung**: Ein Tagebucheintrag (tatsächlich beobachtetes Ereignis einer Pflanze in einem bestimmten Jahr)
- **Ereignis**: Ein geplanter Jahresplan-Eintrag (erwartetes Ereignis einer Pflanze)
- **Ereignisformular**: Das Formular zum Hinzufügen eines neuen Ereignisses, bestehend aus Ereignistyp, Startmonat, optionalem Endmonat und optionalen Detail-Angaben (Anfang/Mitte/Ende)

## Anforderungen

### Anforderung 1: Farbkreis bei Pflanzennamen auf Tagebuch- und Jahresplanseite

**User Story:** Als Gärtner möchte ich, dass die Pflanzennamen auf der Tagebuchseite und der Jahresplanseite genauso dargestellt werden wie auf der Startseite (mit Farbkreis), damit ich Pflanzen visuell schneller zuordnen kann.

#### Akzeptanzkriterien

1. WHEN die Tagebuchseite Beobachtungen anzeigt, THE Tagebuchseite SHALL vor jedem Pflanzennamen einen Farbkreis in der individuellen Farbe der jeweiligen Pflanze darstellen
2. WHEN die Jahresplanseite Ereignisse anzeigt, THE Jahresplanseite SHALL vor jedem Pflanzennamen einen Farbkreis in der individuellen Farbe der jeweiligen Pflanze darstellen
3. THE Farbkreis SHALL die gleiche CSS-Klasse `color-dot` und das gleiche Styling verwenden wie auf der Startseite
4. WHEN eine Pflanze keine individuelle Farbe zugewiesen hat, THE Tagebuchseite und THE Jahresplanseite SHALL keinen Farbkreis vor dem Pflanzennamen anzeigen

### Anforderung 2: Pflanzennamen auf der Startseite als Link zur Detailseite

**User Story:** Als Gärtner möchte ich, dass ein Klick auf den Pflanzennamen in der Pflanzenliste auf der Startseite direkt zur Detailseite der Pflanze führt, damit die Navigation konsistent mit der Tagebuch- und Jahresplanseite ist.

#### Akzeptanzkriterien

1. WHEN ein Pflanzenname in der Pflanzenliste auf der Startseite angezeigt wird, THE Startseite SHALL den Pflanzennamen als anklickbaren Link zur Detailseite (`/plant/<id>/edit`) darstellen
2. THE Startseite SHALL den Farbkreis und den Pflanzennamen gemeinsam als einen Link darstellen
3. THE Startseite SHALL den bestehenden Bearbeiten-Button (✏️) in der Aktionsspalte beibehalten

### Anforderung 3: Ereignisse über die Tagebuchseite eintragen

**User Story:** Als Gärtner möchte ich Ereignisse (Jahresplan-Einträge) direkt über die Tagebuchseite hinzufügen können, damit ich nicht erst zur Detailseite einer Pflanze navigieren muss.

#### Akzeptanzkriterien

1. THE Tagebuchseite SHALL ein Formular zum Hinzufügen eines neuen Ereignisses anzeigen
2. THE Ereignisformular SHALL ein Auswahlfeld für die Pflanze enthalten, das alle aktiven Pflanzen auflistet
3. THE Ereignisformular SHALL die gleichen Felder wie das Ereignisformular auf der Detailseite enthalten: Ereignistyp, Start-Detail, Startmonat, End-Detail und Endmonat
4. WHEN der Ereignistyp kein Zeitraum-Ereignis ist (nicht Blüte oder Ernte), THE Ereignisformular SHALL die Bis-Felder (End-Detail und Endmonat) ausblenden
5. WHEN ein gültiges Ereignis über die Tagebuchseite eingetragen wird, THE Garten-Tracker SHALL das Ereignis speichern und die Tagebuchseite erneut anzeigen
6. IF kein Pflanzenname ausgewählt wird, THEN THE Garten-Tracker SHALL eine Fehlermeldung anzeigen und das Ereignis nicht speichern
7. IF ein ungültiger Ereignistyp übermittelt wird, THEN THE Garten-Tracker SHALL eine Fehlermeldung anzeigen und das Ereignis nicht speichern
