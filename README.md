# 🌱 Garten-Tracker

Eine persönliche Web-App zur Verwaltung von Gartenpflanzen mit Ereigniskalender, Beobachtungslogbuch, phänologischem Kalender und monatlichem Gartenbrief. Läuft als Docker-Container auf einem Raspberry Pi und speichert Daten in SQLite.

![Garten-Tracker Pflanzenliste](docs/garten-tracker.png)

## Funktionen

- **Pflanzenverwaltung** — Kategorie, Typ, Sorte, Lichtbedarf, Lebensdauer, Farbe, Anzahl, Pflanzmonat/-jahr, Beschreibung, Kommentar
- **Erwartete Ereignisse** — Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat, Pflege mit Monatsbereich und optionalem Anfang/Mitte/Ende
- **Beobachtungslogbuch** — tatsächliche Zeiträume pro Jahr festhalten und mit Erwartungen vergleichen
- **Chronologische Listen** — pflanzenübergreifende Beobachtungs- und Ereignislisten, chronologisch sortiert
- **Phänologischer Kalender** — 10 Jahreszeiten pro Jahr erfassen, aktuelle Phase auf der Startseite
- **Pflanzenfotos** — bis zu 5 Fotos pro Pflanze, automatisch auf 640px skaliert, EXIF-Rotation, Hauptbild-Auswahl
- **Gartenkarte** — Kartenbild hochladen, Pflanzen per Klick platzieren, kategoriespezifische Markierungen, Hervorhebung, Filter
- **Pflanze duplizieren** — Satz-Kopie mit allen Stammdaten und Ereignissen
- **Pflanzen deaktivieren** — Inaktiv setzen statt löschen, über Filter wieder einblendbar
- **Filter** — Kategorie, Ereignistyp und Monat auf allen Listen und der Gartenkarte
- **Monatlicher Gartenbrief** — am 1. jeden Monats per E-Mail: was blüht, was geerntet wird, was zurückgeschnitten werden muss — KI-generiert mit Claude, verschickt per Gmail
- **Seed-Scripts** — Datenbank mit recherchierten Pflanzendaten vorausfüllen
- **Responsives Design** — Desktop und Smartphone
- **Komplett auf Deutsch**

## Voraussetzungen

- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/)

## Installation

```bash
git clone https://github.com/achimbarczok/garden-tracker.git
cd garden-tracker
docker build -t garden-tracker .
```

## Container starten

```bash
docker run -d \
  -p 8080:5000 \
  -v garden-data:/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e MAIL_FROM="dein.garten@gmail.com" \
  -e MAIL_TO="deine@email.de" \
  -e MAIL_PASSWORD="xxxx xxxx xxxx xxxx" \
  --name garden-tracker \
  --restart unless-stopped \
  garden-tracker
```

Dann im Browser öffnen: `http://<raspberry-pi-ip>:8080`

Die Umgebungsvariablen für den Gartenbrief (`ANTHROPIC_API_KEY`, `MAIL_*`) sind optional — ohne sie funktioniert die Web-App ganz normal, nur der monatliche Mailversand ist dann nicht möglich.

## Pflanzen vorausfüllen

Beim ersten Start können Pflanzen mit recherchierten Daten eingetragen werden:

```bash
docker exec garden-tracker python seed_plants.py
docker exec garden-tracker python seed_weitere_pflanzen.py
docker exec garden-tracker python seed_wildtulpe_etc.py
```

Die Scripts erkennen Duplikate und überspringen bereits vorhandene Pflanzen.

## Monatlicher Gartenbrief

Das Script `monthly_report.py` liest alle Ereignisse für den aktuellen Monat aus der Datenbank, lässt Claude einen persönlichen Gartenbrief auf Deutsch formulieren und verschickt ihn als HTML-Mail per Gmail.

**Testlauf:**
```bash
docker exec garden-tracker python monthly_report.py
```

**Automatisch per Cron-Job** (am 1. jeden Monats um 8 Uhr):
```bash
crontab -e
# Zeile hinzufügen:
0 8 1 * * docker exec garden-tracker python monthly_report.py >> /home/achim/gartenbrief.log 2>&1
```

**Gmail App-Passwort einrichten:** Unter [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) (2FA muss aktiv sein).

## Update

```bash
cd garden-tracker
git pull
docker build -t garden-tracker .
docker stop garden-tracker && docker rm garden-tracker
docker run -d -p 8080:5000 -v garden-data:/data \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
  -e MAIL_FROM="dein.garten@gmail.com" \
  -e MAIL_TO="deine@email.de" \
  -e MAIL_PASSWORD="xxxx xxxx xxxx xxxx" \
  --name garden-tracker --restart unless-stopped garden-tracker
```

## Daten

Alle Daten werden im Docker-Volume `garden-data` gespeichert und überleben Container-Neustarts und Updates.

**Backup:**
```bash
docker run --rm -v garden-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/garten-backup-$(date +%Y%m%d).tar.gz -C /data .
```

## Lokale Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

DB_PATH=plants.db flask run          # App starten
DB_PATH=plants.db python seed_plants.py  # Beispieldaten laden
pytest                                # Tests ausführen
```

## Technik

- Python 3.12, Flask, Jinja2-Templates
- SQLite (kein ORM, raw SQL)
- Vanilla CSS, kein JavaScript-Framework
- Anthropic Claude API (monatlicher Gartenbrief)
- Gmail SMTP (Mailversand)
- Property-Based Testing mit Hypothesis, Example-Based Tests mit pytest
- Docker (python:3.12-slim)

## Transparenzhinweis

Diese Software wurde vollständig mit KI-Unterstützung entwickelt. Konzeption, Architektur, Code, Templates, Tests und Dokumentation wurden mithilfe von [Kiro](https://kiro.dev) (AI IDE von Amazon) erstellt. Der Entwicklungsprozess folgte einem Spec-Driven-Development-Ansatz: Für jedes Feature wurden zunächst Anforderungen und ein technisches Design erarbeitet, daraus Implementierungsaufgaben abgeleitet und diese dann umgesetzt — jeweils im Dialog zwischen Mensch und KI. Die formale Korrektheit wird durch Property-Based Tests (Hypothesis) abgesichert.
