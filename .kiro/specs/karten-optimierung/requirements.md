# Anforderungsdokument: Karten-Optimierung

## Einleitung

Die bestehende Gartenkarte (`/gartenkarte`) zeigt Pflanzen als einheitliche runde Markierungen auf einem hochgeladenen Gartenbild. Dieses Feature erweitert die Karte um vier Verbesserungen: (1) Filter für Kategorie, Ereignistyp und Monat analog zu den anderen Seiten, (2) größere Markierungen für Sträucher und Gehölze, (3) eckige und größere Markierungen für Gartenpflege-Items, und (4) visuelle Hervorhebung einer ausgewählten Pflanze durch Transparenz aller anderen Markierungen.

## Glossar

- **Gartenkarte**: Die Seite unter `/gartenkarte`, die das Kartenbild mit platzierten Pflanzen-Markierungen anzeigt
- **Markierung**: Ein farbiges HTML-Element (`<div class="karte-marker">`), das eine Pflanze an ihrer gespeicherten Position auf dem Kartenbild darstellt
- **Standard_Markierung**: Eine runde Markierung mit 20px Durchmesser (aktueller Standard für alle Kategorien außer Gehölze und Gartenpflege)
- **Gehölz_Markierung**: Eine runde Markierung mit doppelter Größe (40px Durchmesser) für Pflanzen der Kategorie „Gehölze"
- **Gartenpflege_Markierung**: Eine eckige (quadratische) Markierung mit doppelter Größe (40px) für Pflanzen der Kategorie „Gartenpflege"
- **Filter_Leiste**: Eine Formular-Zeile mit Dropdown-Feldern zum Filtern der angezeigten Markierungen, analog zur Filter-Leiste auf der Pflanzenliste, Beobachtungen- und Ereignisse-Seite
- **Kartenposition**: Ein Datensatz in der Tabelle `kartenpositionen`, der eine Pflanze mit einer relativen X/Y-Position verknüpft
- **Positionierungs_Service**: Die serverseitige Logik in `db.py` und `app.py`, die Kartenpositionen verwaltet
- **Hervorhebung**: Visueller Effekt, bei dem die ausgewählte Pflanze volle Deckkraft behält und alle anderen Markierungen auf 50 % Transparenz gesetzt werden

## Anforderungen

### Anforderung 1: Filter-Leiste auf der Gartenkarte

**User Story:** Als Gärtner möchte ich die Markierungen auf der Gartenkarte nach Kategorie, Ereignistyp und Monat filtern können, damit ich gezielt sehen kann, welche Pflanzen einer bestimmten Gruppe wo im Garten stehen.

#### Akzeptanzkriterien

1. WHILE ein Kartenbild vorhanden ist, THE Gartenkarte SHALL eine Filter_Leiste oberhalb des Kartenbildes anzeigen.
2. THE Filter_Leiste SHALL ein Dropdown-Feld „Kategorie" mit der Option „Alle Kategorien" und allen gültigen Kategorien (Obst, Gemüse, Kräuter, Stauden, Gehölze, Blumen, Gründüngung, Gartenpflege) enthalten.
3. THE Filter_Leiste SHALL ein Dropdown-Feld „Ereignistyp" mit der Option „Alle Ereignisse" und allen gültigen Ereignistypen enthalten.
4. THE Filter_Leiste SHALL ein Dropdown-Feld „Im Monat" mit der Option „Alle Monate" und den zwölf Monatsnamen (Januar bis Dezember) enthalten.
5. WHEN der Benutzer einen Kategorie-Filter auswählt, THE Gartenkarte SHALL ausschließlich Markierungen von Pflanzen anzeigen, deren Kategorie dem gewählten Wert entspricht.
6. WHEN der Benutzer einen Ereignistyp-Filter auswählt, THE Gartenkarte SHALL ausschließlich Markierungen von Pflanzen anzeigen, die mindestens ein Ereignis des gewählten Typs besitzen.
7. WHEN der Benutzer einen Monats-Filter auswählt, THE Gartenkarte SHALL ausschließlich Markierungen von Pflanzen anzeigen, die mindestens ein Ereignis besitzen, dessen Zeitraum (startmonat bis endmonat) den gewählten Monat einschließt.
8. WHEN der Benutzer sowohl Ereignistyp als auch Monat auswählt, THE Gartenkarte SHALL ausschließlich Markierungen von Pflanzen anzeigen, die mindestens ein Ereignis des gewählten Typs besitzen, dessen Zeitraum den gewählten Monat einschließt.
9. WHEN der Benutzer einen Filter ändert, THE Gartenkarte SHALL die Seite per GET-Parameter neu laden und die gewählten Filterwerte in den Dropdown-Feldern beibehalten.
10. THE Filter_Leiste SHALL das gleiche visuelle Muster (Layout, Abstände, Schriftgrößen) verwenden wie die Filter-Leisten auf der Pflanzenliste (`/`), der Beobachtungen-Seite (`/beobachtungen`) und der Ereignisse-Seite (`/ereignisse`).

### Anforderung 2: Vergrößerte Markierungen für Gehölze

**User Story:** Als Gärtner möchte ich, dass Sträucher und Gehölze auf der Karte etwa doppelt so groß wie andere Pflanzen dargestellt werden, damit ich die größeren Pflanzen auf einen Blick von den kleineren unterscheiden kann.

#### Akzeptanzkriterien

1. WHEN eine Kartenposition zu einer Pflanze der Kategorie „Gehölze" gehört, THE Gartenkarte SHALL die Gehölz_Markierung mit doppelter Größe (40px Durchmesser) im Vergleich zur Standard_Markierung (20px) darstellen.
2. WHEN eine Kartenposition zu einer Pflanze der Kategorie „Gehölze" gehört, THE Gartenkarte SHALL die Gehölz_Markierung weiterhin als runden Kreis (border-radius: 50%) darstellen.
3. THE Gartenkarte SHALL die Gehölz_Markierung über eine eigene CSS-Klasse (`karte-marker-gehoelz`) stylen, die die Standard_Markierung-Klasse ergänzt.

### Anforderung 3: Eckige und vergrößerte Markierungen für Gartenpflege

**User Story:** Als Gärtner möchte ich, dass Gartenpflege-Items auf der Karte eckig und doppelt so groß dargestellt werden, damit ich Pflegepunkte (z.B. Kompost, Wasserhahn) visuell klar von Pflanzen unterscheiden kann.

#### Akzeptanzkriterien

1. WHEN eine Kartenposition zu einer Pflanze der Kategorie „Gartenpflege" gehört, THE Gartenkarte SHALL die Gartenpflege_Markierung mit doppelter Größe (40px) im Vergleich zur Standard_Markierung (20px) darstellen.
2. WHEN eine Kartenposition zu einer Pflanze der Kategorie „Gartenpflege" gehört, THE Gartenkarte SHALL die Gartenpflege_Markierung als Quadrat ohne abgerundete Ecken (border-radius: 0) darstellen.
3. THE Gartenkarte SHALL die Gartenpflege_Markierung über eine eigene CSS-Klasse (`karte-marker-gartenpflege`) stylen, die die Standard_Markierung-Klasse ergänzt.

### Anforderung 4: Hervorhebung der ausgewählten Pflanze

**User Story:** Als Gärtner möchte ich, dass beim Auswählen einer Pflanze im Dropdown alle anderen Markierungen auf der Karte halbtransparent werden, damit ich sofort sehe, wo die ausgewählte Pflanze auf der Karte steht.

#### Akzeptanzkriterien

1. WHEN der Benutzer eine Pflanze im Dropdown-Feld auswählt, THE Gartenkarte SHALL alle Markierungen, die nicht zur ausgewählten Pflanze gehören, mit 50 % Deckkraft (opacity: 0.5) darstellen.
2. WHEN der Benutzer eine Pflanze im Dropdown-Feld auswählt, THE Gartenkarte SHALL alle Markierungen der ausgewählten Pflanze mit voller Deckkraft (opacity: 1.0) darstellen.
3. WHEN der Benutzer die Auswahl auf „Pflanze wählen…" (leerer Wert) zurücksetzt, THE Gartenkarte SHALL alle Markierungen mit voller Deckkraft darstellen.
4. THE Gartenkarte SHALL die Hervorhebung über minimales Inline-JavaScript realisieren, das beim Ändern des Dropdown-Wertes (`onchange`) die Deckkraft der Markierungen anpasst.
5. THE Gartenkarte SHALL jeder Markierung ein `data-plant-id`-Attribut zuweisen, damit das JavaScript die Markierungen der ausgewählten Pflanze identifizieren kann.

### Anforderung 5: Erweiterte Datenabfrage für Kartenpositionen

**User Story:** Als Entwickler möchte ich, dass die Datenabfrage für Kartenpositionen die Kategorie der Pflanze mitliefert, damit die Gartenkarte die Markierungen je nach Kategorie unterschiedlich darstellen kann.

#### Akzeptanzkriterien

1. THE Positionierungs_Service SHALL bei der Abfrage der Kartenpositionen zusätzlich die Spalte `kategorie` aus der `plants`-Tabelle zurückgeben.
2. THE Positionierungs_Service SHALL bei der Abfrage der Kartenpositionen zusätzlich die Spalte `aktiv` aus der `plants`-Tabelle zurückgeben, damit inaktive Pflanzen bei Bedarf ausgeblendet werden können.
3. WHEN Filter-Parameter (Kategorie, Ereignistyp, Monat) übergeben werden, THE Positionierungs_Service SHALL die Kartenpositionen serverseitig filtern, bevor die Daten an das Template übergeben werden.
4. THE Gartenkarte SHALL ausschließlich Markierungen für aktive Pflanzen (aktiv = 1) anzeigen, sofern kein expliziter Filter für inaktive Pflanzen gesetzt ist.
