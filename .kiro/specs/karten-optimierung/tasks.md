# Implementation Plan: Karten-Optimierung

## Übersicht

Erweitert die Gartenkarte um Filter-Leiste, kategoriespezifische Markierungen (Gehölze groß+rund, Gartenpflege groß+eckig), Hervorhebung der ausgewählten Pflanze und erweiterte Datenabfrage. Alle Änderungen folgen den bestehenden Architekturmustern (serverseitiges Filtern, Jinja2-Rendering, minimales Inline-JS).

## Tasks

- [x] 1. Erweiterte Datenabfrage in `db.py`
  - [x] 1.1 `get_kartenpositionen()` um `p.kategorie` und `p.aktiv` erweitern
    - SQL-SELECT um `p.kategorie, p.aktiv` ergänzen
    - JOIN bleibt unverändert (`kartenpositionen kp JOIN plants p ON kp.plant_id = p.id`)
    - _Requirements: 5.1, 5.2_

  - [x] 1.2 Property-Test: Erweiterte Abfrage liefert kategorie und aktiv
    - **Property 4: Erweiterte Abfrage liefert kategorie und aktiv**
    - Generiere zufällige Pflanzen mit verschiedenen Kategorien und aktiv-Status, erstelle Positionen, verifiziere dass `kategorie` und `aktiv` korrekt zurückgegeben werden
    - **Validates: Requirements 5.1, 5.2**

- [x] 2. Filter-Logik in `app.py`
  - [x] 2.1 `gartenkarte_page()` um Filter-Logik erweitern
    - Nur aktive Pflanzen anzeigen: `positionen = [p for p in positionen if p.get("aktiv", 1) == 1]`
    - GET-Parameter `kategorie`, `ereignis`, `monat` aus `request.args` lesen
    - Kategorie-Filter: Positionen nach `kategorie` filtern
    - Ereignistyp-/Monats-Filter: `get_all_ereignisse()` laden, `_filter_plant_ids_by_ereignis()` aufrufen, Positionen filtern
    - Template-Variablen ergänzen: `german_months`, `valid_kategorien`, `valid_ereignistypen`, `filter_kategorie`, `filter_ereignis`, `filter_monat`
    - _Requirements: 1.5, 1.6, 1.7, 1.8, 1.9, 5.3, 5.4_

  - [x] 2.2 Hilfsfunktion `_filter_plant_ids_by_ereignis()` implementieren
    - Filtert Ereignisliste nach Ereignistyp und/oder Monat (Zeitraum startmonat–endmonat)
    - Gibt `set` von `plant_id`s zurück
    - Gleiche Logik wie in `ereignisse_page()` für Monats-Filterung
    - _Requirements: 1.6, 1.7, 1.8_

  - [x] 2.3 Property-Test: Filterung liefert nur passende Positionen
    - **Property 1: Filterung liefert nur passende Positionen**
    - Generiere zufällige Pflanzen mit Kategorien, Ereignissen und Kartenpositionen, wende zufällige Filterkombinationen an, verifiziere dass nur passende Positionen zurückgegeben werden
    - **Validates: Requirements 1.5, 1.6, 1.7, 1.8, 5.3**

  - [x] 2.4 Property-Test: Nur aktive Pflanzen auf der Karte
    - **Property 5: Nur aktive Pflanzen auf der Karte**
    - Generiere zufällige Pflanzen (aktiv/inaktiv) mit Positionen, rufe Route auf, verifiziere dass nur aktive Pflanzen-Markierungen im HTML erscheinen
    - **Validates: Requirements 5.4**

- [x] 3. Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Template und CSS für Markierungen und Filter-Leiste
  - [x] 4.1 CSS-Klassen für Gehölze und Gartenpflege in `static/style.css` hinzufügen
    - `.karte-marker-gehoelz`: `width: 40px; height: 40px; border-radius: 50%;`
    - `.karte-marker-gartenpflege`: `width: 40px; height: 40px; border-radius: 0;`
    - Mobile-Anpassung im `@media (max-width: 599px)` Block: beide Klassen auf `32px`
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 3.2, 3.3_

  - [x] 4.2 Filter-Leiste in `templates/gartenkarte.html` einfügen
    - `<div class="card">` mit `<form class="filter-bar">` oberhalb des Karten-Containers, nur wenn `kartenbild` vorhanden
    - Dropdown „Kategorie" mit „Alle Kategorien" + `valid_kategorien`
    - Dropdown „Ereignistyp" mit „Alle Ereignisse" + `valid_ereignistypen`
    - Dropdown „Im Monat" mit „Alle Monate" + `german_months` (1–12)
    - `onchange="this.form.submit()"` auf jedem Dropdown
    - Gewählte Filterwerte per `selected`-Attribut beibehalten
    - „Filter zurücksetzen"-Link wenn mindestens ein Filter aktiv
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.9, 1.10_

  - [x] 4.3 Markierungen in `templates/gartenkarte.html` erweitern
    - Kategoriespezifische CSS-Klassen: `karte-marker-gehoelz` für Gehölze, `karte-marker-gartenpflege` für Gartenpflege
    - `data-plant-id="{{ pos.plant_id }}"` Attribut auf jeder Markierung
    - _Requirements: 2.3, 3.3, 4.5_

  - [x] 4.4 Hervorhebungs-JavaScript in `templates/gartenkarte.html` ergänzen
    - Im bestehenden Inline-Script: `change`-Event auf dem Pflanzen-Dropdown
    - Wenn Pflanze gewählt: alle `.karte-marker` mit `data-plant-id != gewählte_id` auf `opacity: 0.5`, gewählte auf `opacity: 1`
    - Wenn Auswahl zurückgesetzt: alle Markierungen auf `opacity: 1`
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [x] 4.5 Property-Test: Kategoriespezifische Marker-Klassen
    - **Property 2: Kategoriespezifische Marker-Klassen**
    - Generiere zufällige Pflanzen mit verschiedenen Kategorien und Positionen, rendere die Seite, verifiziere korrekte CSS-Klassen im HTML
    - **Validates: Requirements 2.1, 2.3, 3.1, 3.3**

  - [x] 4.6 Property-Test: data-plant-id Attribut auf Markierungen
    - **Property 3: data-plant-id Attribut auf Markierungen**
    - Generiere zufällige Pflanzen mit Positionen, rendere die Seite, verifiziere `data-plant-id`-Attribute
    - **Validates: Requirements 4.5**

- [x] 5. Final Checkpoint
  - Ensure all tests pass, ask the user if questions arise.

## Hinweise

- Tasks mit `*` sind optional und können für ein schnelleres MVP übersprungen werden
- Jeder Task referenziert spezifische Anforderungen für Nachvollziehbarkeit
- Property-Tests validieren universelle Korrektheitseigenschaften aus dem Design-Dokument
- Die bestehende Testinfrastruktur aus `test_gartenkarte_properties.py` wird als Vorlage verwendet
