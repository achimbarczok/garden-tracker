# Product: Garten-Tracker

A personal garden management web app (German-language) for tracking plants, seasonal events, observations, and phenological seasons. Designed to run as a Docker container on a Raspberry Pi with persistent SQLite storage.

## Core Features
- Plant management: name, category, type, variety, light needs, lifespan, color, quantity, planting date, description, comments
- Expected events per plant (Blüte, Ernte, Düngen, Rückschnitt, Vorkultur, Auspflanzen, Direktsaat, Pflege) with month ranges and optional Anfang/Mitte/Ende detail
- Observation log: record actual event timings per year for comparison with expectations
- Chronological lists: cross-plant observation list (`/beobachtungen`) and event list (`/ereignisse`), sorted by computed sort value (month × 100 + detail offset), with category/event type/month filters
- Phenological calendar: 10 phenological seasons per year (Vorfrühling through Winter), current phase shown on homepage
- Plant photos: up to 5 photos per plant, auto-resized to 640px, EXIF rotation, Hauptbild selection
- Garden map (`/gartenkarte`): upload a garden image, click to place plants with percentage-based coordinates, colored markers with tooltips, filter bar (category/event type/month), category-specific marker sizes (Gehölze large+round, Gartenpflege large+square), plant highlighting via dropdown selection, only active plants shown
- Plant duplication (Satz copy with all master data and events)
- Deactivate plants instead of deleting — data preserved, hidden from default list, reactivatable via filter
- Filtering by category, event type, and month on plant list, observation list, event list, and garden map
- Seed scripts for pre-populating the database with researched plant data

## Language & Locale
- The entire UI, all error messages, labels, and user-facing text are in German
- All new features, validation messages, and UI copy must be written in German
- Domain terms use German naming: Pflanze, Ereignis, Beobachtung, Phänologie, Lichtbedarf, Lebensdauer, Kategorie, etc.

## Deployment
- Runs on Raspberry Pi via Docker
- SQLite database stored in a Docker volume at `/data/plants.db`
- Default port 5000 (configurable via `PORT` env var)
