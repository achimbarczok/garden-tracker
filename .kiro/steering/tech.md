# Tech Stack

## Backend
- Python 3.12
- Flask (server-side rendered, no API/SPA)
- SQLite with `sqlite3` stdlib module (no ORM)
- Jinja2 templates
- Pillow (image processing: EXIF rotation, resize, JPEG conversion)

## Frontend
- Server-rendered HTML via Jinja2 templates
- Vanilla CSS (no preprocessor, no CSS framework)
- No JavaScript frameworks — minimal inline JS only (e.g. `onchange`, `confirm()`)
- Responsive design with mobile-first media queries

## Infrastructure
- Docker (python:3.12-slim base image, non-root user)
- SQLite database file at path from `DB_PATH` env var (default `/data/plants.db`)
- Docker volume for persistent data (DB + `fotos/` + `karte/` directories)

## Testing
- pytest
- hypothesis (property-based testing)

## Common Commands

```bash
# Install dependencies (in venv)
pip install -r requirements.txt

# Run tests
pytest

# Run the app locally
DB_PATH=plants.db flask run

# Seed the database with sample plants
DB_PATH=plants.db python seed_plants.py

# Docker build & run
docker build -t garden-tracker .
docker run -d -p 8080:5000 -v garden-data:/data --name garden-tracker garden-tracker

# Backup data from Docker volume
docker run --rm -v garden-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/garten-backup-$(date +%Y%m%d).tar.gz -C /data .
```

## Key Environment Variables
- `DB_PATH` — path to SQLite database file (default: `/data/plants.db`)
- `PORT` — Flask server port (default: `5000`)
