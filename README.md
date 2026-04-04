# Garden Tracker

Eine minimalistische Web-App zur Verwaltung von Gartenpflanzen. Läuft als Docker-Container auf einem Raspberry Pi und speichert Daten in SQLite.

## Voraussetzungen

- [Docker](https://docs.docker.com/get-docker/) mit Buildx-Plugin
- [Git](https://git-scm.com/)

## Repository klonen

```bash
git clone <repo-url>
cd garden-tracker
```

## Docker-Image bauen (linux/arm64)

```bash
docker buildx build --platform linux/arm64 -t garden-tracker .
```

## Container starten

```bash
docker run -d -p 8080:5000 -v garden-data:/data --name garden-tracker garden-tracker
```

## Port anpassen

Der interne Port ist standardmäßig `5000`. Um ihn zu ändern, die Umgebungsvariable `PORT` setzen:

```bash
docker run -d -p 8080:5000 -e PORT=5000 -v garden-data:/data --name garden-tracker garden-tracker
```

Den Host-Port (`8080`) nach Bedarf anpassen.

## App im Browser öffnen

```
http://<raspberry-pi-ip>:8080
```

## Container stoppen und entfernen

```bash
docker stop garden-tracker && docker rm garden-tracker
```

## Daten

Alle Pflanzendaten werden im Docker-Volume `garden-data` gespeichert und bleiben auch nach einem Neustart des Containers erhalten.
