# 🌱 Garten-Tracker

Eine Web-App zur Verwaltung von Gartenpflanzen mit Ereigniskalender, Beobachtungslogbuch und phänologischem Kalender. Läuft als Docker-Container auf einem Raspberry Pi und speichert Daten in SQLite.

## Funktionen

- Pflanzenverwaltung mit Kategorie, Sorte, Lichtbedarf, Lebensdauer, Farbe, Anzahl
- Erwartete Ereignisse pro Pflanze (Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat)
- Beobachtungslogbuch — tatsächliche Zeiträume pro Jahr festhalten
- Phänologischer Kalender — 10 Jahreszeiten pro Jahr erfassen, aktuelle Phase auf der Startseite
- Pflanzenbeschreibung als Referenzinfo
- Filter nach Kategorie, Ereignistyp und Monat
- Monatsangaben mit optionalem Anfang/Mitte/Ende
- Responsives Design für Desktop und Smartphone
- Komplett auf Deutsch

## Voraussetzungen

- [Docker](https://docs.docker.com/get-docker/)
- [Git](https://git-scm.com/)

## Installation auf dem Raspberry Pi

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
  --name garden-tracker \
  --restart unless-stopped \
  garden-tracker
```

## App öffnen

```
http://<raspberry-pi-ip>:8080
```

## Port anpassen

```bash
docker run -d -p 9090:5000 -e PORT=5000 -v garden-data:/data --name garden-tracker --restart unless-stopped garden-tracker
```

## Pflanzen vorausfüllen

Beim ersten Start können Pflanzen mit recherchierten Daten eingetragen werden:

```bash
docker exec garden-tracker python seed_plants.py
```

## Update

```bash
cd ~/docker/garden-tracker
git pull
docker build -t garden-tracker .
docker stop garden-tracker && docker rm garden-tracker
docker run -d -p 8080:5000 -v garden-data:/data --name garden-tracker --restart unless-stopped garden-tracker
```

## Container stoppen

```bash
docker stop garden-tracker && docker rm garden-tracker
```

## Daten

Alle Daten werden im Docker-Volume `garden-data` gespeichert und überleben Container-Neustarts und Updates.
