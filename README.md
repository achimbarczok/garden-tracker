# 🌱 Garten-Tracker

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![Docker](https://img.shields.io/badge/Docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Eine persönliche Web-App zur Verwaltung von Gartenpflanzen mit Ereigniskalender, Beobachtungslogbuch, phänologischem Kalender, Gartenkarte und KI-gestütztem monatlichem Gartenbrief. Läuft als Docker-Container auf einem Raspberry Pi mit SQLite-Datenbank.

![Garten-Tracker Pflanzenliste](docs/garten-tracker.png)

## Funktionen

| Feature | Beschreibung |
|---------|-------------|
| 🌿 Pflanzenverwaltung | Kategorie, Typ, Sorte, Lichtbedarf, Lebensdauer, Farbe, Anzahl, Pflanzmonat/-jahr, Beschreibung |
| 🗓️ Jahresplan | Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat mit Monatsbereich |
| 📝 Beobachtungslogbuch | Tatsächliche Zeiträume pro Jahr festhalten und mit Erwartungen vergleichen |
| 📋 Chronologische Listen | Pflanzenübergreifende Beobachtungs- und Ereignislisten |
| 🍃 Phänologischer Kalender | 10 Jahreszeiten pro Jahr, aktuelle Phase auf der Startseite |
| 📷 Pflanzenfotos | Bis zu 5 Fotos pro Pflanze, automatisch skaliert, EXIF-Rotation |
| 🗺️ Gartenkarte | Kartenbild hochladen, Pflanzen per Klick platzieren, Filter |
| 🤖 KI-Autofill | Pflanzendaten per KI generieren (Beschreibung, Ereignisse, Kategorie) |
| 📬 Monatlicher Gartenbrief | KI-generierte E-Mail am 1. jeden Monats mit allen anstehenden Aufgaben |
| 📋 Pflanze duplizieren | Satz-Kopie mit allen Stammdaten und Ereignissen |
| 💤 Pflanzen deaktivieren | Inaktiv setzen statt löschen, über Filter wieder einblendbar |
| 🔍 Filter | Kategorie, Ereignistyp und Monat auf allen Listen und der Gartenkarte |

## Schnellstart

### Voraussetzungen

- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/)
- Optional: [Anthropic API-Key](https://console.anthropic.com/) für KI-Features

### Installation & Start

```bash
git clone https://github.com/achimbarczok/garden-tracker.git
cd garden-tracker
docker build -t garden-tracker .

docker run -d \
  -p 8080:5000 \
  -v garden-data:/data \
  --env-file .env \
  --name garden-tracker \
  --restart unless-stopped \
  garden-tracker
```

Dann im Browser öffnen: `http://<raspberry-pi-ip>:8080`

### Konfiguration (.env)

Erstelle eine `.env`-Datei im Projektverzeichnis:

```env
# Pflicht für KI-Features (Autofill + Gartenbrief)
ANTHROPIC_API_KEY=sk-ant-dein-key-hier

# Pflicht für den monatlichen Gartenbrief
MAIL_FROM=absender@gmail.com
MAIL_TO=empfaenger@email.de
MAIL_PASSWORD=xxxx xxxx xxxx xxxx
```

Ohne diese Variablen funktioniert die Web-App normal — nur KI-Autofill und Gartenbrief sind dann nicht verfügbar.

<details>
<summary>Alle Umgebungsvariablen</summary>

| Variable | Beschreibung | Default |
|----------|-------------|---------|
| `DB_PATH` | Pfad zur SQLite-Datenbank | `/data/plants.db` |
| `PORT` | Flask-Server-Port | `5000` |
| `LLM_PROVIDER` | LLM-Provider: `claude` oder `mistral` | `claude` |
| `LLM_MODEL` | Modellname (optional) | `claude-sonnet-4-6` |
| `ANTHROPIC_API_KEY` | Anthropic API-Key | – |
| `MISTRAL_API_KEY` | Mistral API-Key (Alternative) | – |
| `MAIL_FROM` | Absender-Gmail-Adresse | – |
| `MAIL_TO` | Empfänger (kommasepariert) | – |
| `MAIL_PASSWORD` | Gmail App-Passwort | – |
| `MAIL_SMTP_HOST` | SMTP-Server | `smtp.gmail.com` |
| `MAIL_SMTP_PORT` | SMTP-Port | `587` |

</details>

## KI-Autofill

Beim Hinzufügen oder Bearbeiten einer Pflanze kann per Button „🤖 KI-Vorschlag" eine KI-gestützte Befüllung der Felder ausgelöst werden. Die KI generiert Beschreibung, Kategorie, Lichtbedarf, Lebensdauer und erwartete Ereignisse basierend auf dem Pflanzennamen.

Der Button erscheint nur, wenn ein API-Key konfiguriert ist.

## Monatlicher Gartenbrief

Am 1. jeden Monats wird automatisch eine HTML-Mail verschickt mit:
- Aufgaben aus dem Jahresplan (Rückschnitt, Aussaat, Ernte etc.)
- KI-generierte Pflanz-Tipps für den Monat
- Motivierender Gartenbrief auf Deutsch

**Testlauf:**
```bash
docker exec garden-tracker python monthly_report.py
```

**Cron-Job einrichten** (am 1. jeden Monats um 8 Uhr):
```bash
crontab -e
# Zeile hinzufügen:
0 8 1 * * docker exec garden-tracker python monthly_report.py >> ~/gartenbrief.log 2>&1
```

**Gmail App-Passwort:** Unter [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) erstellen (2FA muss aktiv sein).

## Update

```bash
cd garden-tracker
git pull
docker build -t garden-tracker .
docker stop garden-tracker && docker rm garden-tracker
docker run -d -p 8080:5000 -v garden-data:/data --env-file .env \
  --name garden-tracker --restart unless-stopped garden-tracker
```

## Datensicherung

Alle Daten liegen im Docker-Volume `garden-data` und überleben Container-Neustarts.

```bash
# Backup erstellen
docker run --rm -v garden-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/garten-backup-$(date +%Y%m%d).tar.gz -C /data .

# Backup wiederherstellen
docker run --rm -v garden-data:/data -v $(pwd):/backup alpine \
  tar xzf /backup/garten-backup-YYYYMMDD.tar.gz -C /data
```

## Lokale Entwicklung

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

DB_PATH=plants.db flask run   # App starten
pytest                         # Tests ausführen
```

## Techstack

- **Backend:** Python 3.12, Flask, SQLite (raw SQL, kein ORM)
- **Frontend:** Jinja2-Templates, Vanilla CSS, minimales Inline-JS
- **KI:** Anthropic Claude API (alternativ Mistral)
- **Infrastruktur:** Docker (python:3.12-slim), Gmail SMTP
- **Testing:** pytest, Hypothesis (Property-Based Testing)

## Projektstruktur

```
├── app.py              # Flask-App: Routen, Validierung, Autofill-Endpunkt
├── db.py               # Datenbankschicht: Schema, Migrationen, CRUD
├── llm.py              # Gemeinsames LLM-Modul (Claude/Mistral)
├── monthly_report.py   # Monatlicher Gartenbrief (CLI-Script)
├── templates/          # Jinja2-Templates (6 Seiten)
├── static/style.css    # Styles
└── tests/              # pytest + Hypothesis
```

## Mitwirken

Pull Requests sind willkommen. Bitte beachten:
- UI-Texte und Fehlermeldungen auf Deutsch
- Kein JavaScript-Framework — nur minimales Inline-JS
- Tests mit `pytest` ausführen vor dem PR

## Lizenz

MIT

## Transparenzhinweis

Diese Software wurde vollständig mit KI-Unterstützung entwickelt. Konzeption, Architektur, Code, Templates, Tests und Dokumentation wurden mithilfe von [Kiro](https://kiro.dev) (AI IDE von Amazon) erstellt. Der Entwicklungsprozess folgte einem Spec-Driven-Development-Ansatz mit Property-Based Testing (Hypothesis) zur Absicherung der Korrektheit.
