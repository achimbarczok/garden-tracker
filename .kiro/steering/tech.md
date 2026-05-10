# Tech Stack

## Backend
- Python 3.12
- Flask (server-side rendered, no API/SPA)
- SQLite with `sqlite3` stdlib module (no ORM)
- Jinja2 templates
- Pillow (image processing: EXIF rotation, resize, JPEG conversion)
- anthropic (Claude API client for monthly garden report)

## Frontend
- Server-rendered HTML via Jinja2 templates
- Vanilla CSS (no preprocessor, no CSS framework)
- No JavaScript frameworks — minimal inline JS only (e.g. `onchange`, `confirm()`)
- Responsive design with mobile-first media queries

## Infrastructure
- Docker (python:3.12-slim base image, non-root user)
- SQLite database file at path from `DB_PATH` env var (default `/data/plants.db`)
- Docker volume for persistent data (DB + `fotos/` + `karte/` directories)
- Cron job on host for monthly report (`0 8 1 * * docker exec garden-tracker python monthly_report.py`)
- Gmail SMTP (smtp.gmail.com:587, TLS) for outbound email
- Anthropic API (HTTPS) for AI-generated report text

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

# Send monthly garden report (test run)
DB_PATH=plants.db ANTHROPIC_API_KEY=... MAIL_FROM=... MAIL_TO=... MAIL_PASSWORD=... python monthly_report.py

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
- `LLM_PROVIDER` — LLM provider to use: `claude` (default) or `mistral`
- `LLM_MODEL` — specific model name (optional, provider defaults apply)
- `ANTHROPIC_API_KEY` — Anthropic API key for Claude (monthly report + autofill)
- `MISTRAL_API_KEY` — Mistral API key (alternative LLM provider for autofill + report)
- `MAIL_FROM` — sender Gmail address for monthly report
- `MAIL_TO` — recipient email address for monthly report
- `MAIL_PASSWORD` — Gmail App Password (not the regular Gmail password)
- `MAIL_SMTP_HOST` — SMTP server (default: `smtp.gmail.com`)
- `MAIL_SMTP_PORT` — SMTP port (default: `587`)
