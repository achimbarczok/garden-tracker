# Project Structure

```
├── app.py              # Flask application — all routes, validation, helpers, constants
├── db.py               # Database layer — init, migrations (V1–V6), all CRUD functions
├── conftest.py         # Root pytest config — ensures project root on sys.path
├── seed_plants.py      # One-time seed script for sample plant data
├── seed_neue_pflanzen.py # Additional seed script for more plant data
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition (python:3.12-slim, non-root user)
├── templates/
│   ├── base.html       # Base layout (header, nav with 4 links, page wrapper)
│   ├── index.html      # Homepage — plant list, filters, add-plant form
│   ├── edit.html       # Plant detail/edit — events, observations, photos, delete
│   ├── beobachtungen.html # Chronological observation list with filters
│   ├── ereignisse.html # Chronological event list with filters
│   ├── phaenologie.html # Phenological calendar page
│   └── gartenkarte.html # Garden map — image upload, click-to-place markers, inline JS
├── static/
│   └── style.css       # All styles (CSS custom properties, responsive, garden map)
└── tests/
    ├── test_routes.py  # Route/endpoint tests using Flask test client (30 tests)
    ├── test_startup.py # Startup error handling tests
    ├── test_pflanze_inaktiv_properties.py  # PBT — plant deactivation
    ├── test_chronologische_listen_properties.py # PBT — chronological lists
    ├── test_pflanzen_fotos_properties.py   # PBT — photo upload/management
    ├── test_pflanzen_fotos.py             # Example tests — photo features
    └── test_gartenkarte_properties.py     # PBT — garden map (12 properties)
```

## Architecture Patterns

- Two-file backend: `app.py` (routes + validation) and `db.py` (data access)
- No ORM — raw SQL via `sqlite3`, `sqlite3.Row` for dict-like access
- Schema migrations handled inline in `db.py` `_migrate()` with version tracking (currently V6)
- `init_db()` creates tables + runs migrations on app startup; failure logs a German error and exits
- DB connections: request-scoped via Flask `g` inside requests, fresh connections outside (tests, scripts)
- Templates extend `base.html`; forms use POST with redirect (PRG pattern)
- Shared helpers: `_parse_plant_form()` for add/edit validation, `_process_image()` for photo/map image processing
- Validation constants (valid categories, event types, light levels, etc.) defined at module level in `app.py`
- `_safe_next()` helper for safe redirect targets after form submissions
- Image files stored in Docker volume subdirectories: `fotos/` (plant photos), `karte/` (garden map)

## Conventions
- German domain terminology throughout code: `ereignis`, `beobachtung`, `pflanze`, `lichtbedarf`, `lebensdauer`, `kategorie`, `phaenologie`, `sortierwert`, `kartenbild`, `kartenposition`
- Route naming follows resource pattern: `/plant/<id>/edit`, `/plant/<id>/ereignis/add`
- Cross-plant list routes: `/beobachtungen`, `/ereignisse` (flat lists with JOIN queries)
- Garden map routes: `/gartenkarte`, `/gartenkarte/bild/upload`, `/gartenkarte/position/add`
- Error responses return the same template with an `error` variable and HTTP 400
- Tests use `tmp_path` + `monkeypatch` to isolate the database per test
- Property-based tests use `tempfile.TemporaryDirectory()` + `importlib.reload()` for DB isolation
- `FOREIGN_KEYS = ON` pragma enforced on every connection
- Indexes on all foreign key columns (V6 migration)
- Sort value calculation: `monat × 100 + offset` (Anfang=5, Mitte=15, Ende=25, None=15) via `berechne_sortierwert()` pure function

## Database Tables (Schema V6)
- `plants` — plant master data (name, type, variety, kategorie, farbe, aktiv, etc.)
- `ereignisse` — expected events per plant (indexed on plant_id)
- `beobachtungen` — actual observations per plant per year (indexed on plant_id)
- `phaenologie` — phenological season entries per year
- `fotos` — plant photos with Hauptbild flag (indexed on plant_id)
- `kartenbild` — single garden map image entry (max 1 row)
- `kartenpositionen` — plant positions on garden map as percentage coordinates (indexed on plant_id)
- `schema_version` — migration version tracking
