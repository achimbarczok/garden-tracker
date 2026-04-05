# Anforderungsdokument: Chronologische Listen

## Einleitung

Der Garten-Tracker erhält zwei neue, pflanzenunabhängige Ansichten: eine chronologisch sortierte Liste aller Beobachtungen und eine chronologisch sortierte Liste aller erwarteten Ereignisse. Beide Listen bieten dieselben Filtermöglichkeiten wie die Pflanzenübersicht (Kategorie, Monat, Ereignistyp). Die Sortierung basiert auf dem Startmonat bzw. dem start_detail (Anfang/Mitte/Ende) der Einträge. Einträge ohne Angabe von Anfang/Mitte/Ende werden chronologisch in die Mitte des Monats einsortiert.

## Glossar

- **Beobachtungsliste**: Neue Seite, die alle Beobachtungen aller aktiven Pflanzen chronologisch sortiert anzeigt
- **Ereignisliste**: Neue Seite, die alle erwarteten Ereignisse aller aktiven Pflanzen chronologisch sortiert anzeigt
- **Sortierwert**: Numerischer Wert zur chronologischen Einordnung, berechnet aus Startmonat und start_detail
- **Detail-Angabe**: Optionale Präzisierung eines Monats durch "Anfang", "Mitte" oder "Ende"
- **Kategorie**: Pflanzen-Kategorie (Obst, Gemüse, Kräuter, Stauden, Sträucher, Bäume, Blumen, Gründüngung)
- **Ereignistyp**: Art des Ereignisses (Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat)
- **Navigation**: Hauptnavigation im Header der Anwendung

## Anforderungen

### Anforderung 1: Navigation zu den chronologischen Listen

**User Story:** Als Gärtner möchte ich die chronologischen Listen über die Navigation erreichen, damit ich schnell zwischen Pflanzenübersicht und den neuen Ansichten wechseln kann.

#### Akzeptanzkriterien

1. THE Navigation SHALL zwei zusätzliche Links anzeigen: "🔍 Beobachtungen" und "🗓️ Ereignisse"
2. WHEN der Nutzer auf "🔍 Beobachtungen" klickt, THE Navigation SHALL zur Beobachtungsliste unter `/beobachtungen` weiterleiten
3. WHEN der Nutzer auf "🗓️ Ereignisse" klickt, THE Navigation SHALL zur Ereignisliste unter `/ereignisse` weiterleiten

### Anforderung 2: Chronologische Beobachtungsliste

**User Story:** Als Gärtner möchte ich alle Beobachtungen chronologisch sortiert sehen, damit ich einen pflanzenübergreifenden Überblick über tatsächliche Ereignisse habe.

#### Akzeptanzkriterien

1. WHEN die Seite `/beobachtungen` aufgerufen wird, THE Beobachtungsliste SHALL alle Beobachtungen aller aktiven Pflanzen anzeigen
2. THE Beobachtungsliste SHALL jede Beobachtung mit Pflanzenname, Jahr, Ereignistyp, Zeitraum (Startmonat mit Detail bis Endmonat mit Detail) und Notiz anzeigen
3. THE Beobachtungsliste SHALL die Beobachtungen aufsteigend nach Sortierwert des Startmonats ordnen
4. WHEN zwei Beobachtungen denselben Sortierwert haben, THE Beobachtungsliste SHALL diese alphabetisch nach Pflanzenname ordnen

### Anforderung 3: Chronologische Ereignisliste

**User Story:** Als Gärtner möchte ich alle erwarteten Ereignisse chronologisch sortiert sehen, damit ich einen pflanzenübergreifenden Überblick über anstehende Gartenarbeiten habe.

#### Akzeptanzkriterien

1. WHEN die Seite `/ereignisse` aufgerufen wird, THE Ereignisliste SHALL alle erwarteten Ereignisse aller aktiven Pflanzen anzeigen
2. THE Ereignisliste SHALL jedes Ereignis mit Pflanzenname, Ereignistyp und Zeitraum (Startmonat mit Detail bis Endmonat mit Detail) anzeigen
3. THE Ereignisliste SHALL die Ereignisse aufsteigend nach Sortierwert des Startmonats ordnen
4. WHEN zwei Ereignisse denselben Sortierwert haben, THE Ereignisliste SHALL diese alphabetisch nach Pflanzenname ordnen

### Anforderung 4: Berechnung des Sortierwerts

**User Story:** Als Gärtner möchte ich, dass Einträge korrekt chronologisch einsortiert werden, auch wenn die Detail-Angabe fehlt.

#### Akzeptanzkriterien

1. WHEN ein Eintrag die Detail-Angabe "Anfang" hat, THE Sortierwert SHALL als Monat × 100 + 5 berechnet werden
2. WHEN ein Eintrag die Detail-Angabe "Mitte" hat, THE Sortierwert SHALL als Monat × 100 + 15 berechnet werden
3. WHEN ein Eintrag die Detail-Angabe "Ende" hat, THE Sortierwert SHALL als Monat × 100 + 25 berechnet werden
4. WHEN ein Eintrag keine Detail-Angabe hat, THE Sortierwert SHALL als Monat × 100 + 15 berechnet werden (Einordnung in die Mitte)

### Anforderung 5: Filter für die Beobachtungsliste

**User Story:** Als Gärtner möchte ich die Beobachtungsliste nach Kategorie, Monat und Ereignistyp filtern, damit ich gezielt nach bestimmten Beobachtungen suchen kann.

#### Akzeptanzkriterien

1. THE Beobachtungsliste SHALL eine Filterleiste mit Dropdowns für Kategorie, Ereignistyp und Monat anzeigen
2. WHEN der Nutzer eine Kategorie auswählt, THE Beobachtungsliste SHALL nur Beobachtungen von Pflanzen dieser Kategorie anzeigen
3. WHEN der Nutzer einen Ereignistyp auswählt, THE Beobachtungsliste SHALL nur Beobachtungen dieses Ereignistyps anzeigen
4. WHEN der Nutzer einen Monat auswählt, THE Beobachtungsliste SHALL nur Beobachtungen anzeigen, deren Zeitraum den gewählten Monat einschließt (startmonat ≤ Monat ≤ endmonat)
5. WHEN mehrere Filter gleichzeitig gesetzt sind, THE Beobachtungsliste SHALL nur Beobachtungen anzeigen, die alle Filterkriterien erfüllen
6. WHEN mindestens ein Filter aktiv ist, THE Beobachtungsliste SHALL einen Link "Filter zurücksetzen" anzeigen

### Anforderung 6: Filter für die Ereignisliste

**User Story:** Als Gärtner möchte ich die Ereignisliste nach Kategorie, Monat und Ereignistyp filtern, damit ich gezielt nach bestimmten erwarteten Ereignissen suchen kann.

#### Akzeptanzkriterien

1. THE Ereignisliste SHALL eine Filterleiste mit Dropdowns für Kategorie, Ereignistyp und Monat anzeigen
2. WHEN der Nutzer eine Kategorie auswählt, THE Ereignisliste SHALL nur Ereignisse von Pflanzen dieser Kategorie anzeigen
3. WHEN der Nutzer einen Ereignistyp auswählt, THE Ereignisliste SHALL nur Ereignisse dieses Ereignistyps anzeigen
4. WHEN der Nutzer einen Monat auswählt, THE Ereignisliste SHALL nur Ereignisse anzeigen, deren Zeitraum den gewählten Monat einschließt (startmonat ≤ Monat ≤ endmonat)
5. WHEN mehrere Filter gleichzeitig gesetzt sind, THE Ereignisliste SHALL nur Ereignisse anzeigen, die alle Filterkriterien erfüllen
6. WHEN mindestens ein Filter aktiv ist, THE Ereignisliste SHALL einen Link "Filter zurücksetzen" anzeigen

### Anforderung 7: Leere Zustände

**User Story:** Als Gärtner möchte ich eine hilfreiche Meldung sehen, wenn keine Einträge vorhanden sind oder die Filter keine Ergebnisse liefern.

#### Akzeptanzkriterien

1. WHEN keine Beobachtungen vorhanden sind, THE Beobachtungsliste SHALL die Meldung "Noch keine Beobachtungen vorhanden." anzeigen
2. WHEN keine Ereignisse vorhanden sind, THE Ereignisliste SHALL die Meldung "Noch keine Ereignisse vorhanden." anzeigen
3. WHEN die aktiven Filter keine Ergebnisse liefern, THE Beobachtungsliste SHALL die Meldung "Keine Beobachtungen gefunden." und einen Link zum Zurücksetzen der Filter anzeigen
4. WHEN die aktiven Filter keine Ergebnisse liefern, THE Ereignisliste SHALL die Meldung "Keine Ereignisse gefunden." und einen Link zum Zurücksetzen der Filter anzeigen

### Anforderung 8: Verlinkung zur Pflanze

**User Story:** Als Gärtner möchte ich von einem Eintrag in der chronologischen Liste direkt zur zugehörigen Pflanze navigieren können, damit ich Details einsehen oder bearbeiten kann.

#### Akzeptanzkriterien

1. THE Beobachtungsliste SHALL den Pflanzennamen jeder Beobachtung als Link zur Bearbeitungsseite der zugehörigen Pflanze (`/plant/<id>/edit`) darstellen
2. THE Ereignisliste SHALL den Pflanzennamen jedes Ereignisses als Link zur Bearbeitungsseite der zugehörigen Pflanze (`/plant/<id>/edit`) darstellen
