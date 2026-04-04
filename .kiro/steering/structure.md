# Project Structure

```
├── app.py              # Flask application — all routes, validation, constants
├── db.py               # Database layer — init, migrations, all CRUD functions
├── conftest.py         # Root pytest config — ensures project root on sys.path
├── seed_plants.py      # One-time seed script for sample plant data
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container definition
├── templates/
│   ├── base.html       # Base layout (header, nav, page wrapper)
│   ├── index.html      # Homepage — plant list, filters, add-plant form
│   ├── edit.html       # Plant detail/edit — events, observations, delete
│   └── phaenologie.html # Phenological calendar page
├── static/
│   └── style.css       # All styles (CSS custom properties, responsive)
└── tests/
    ├── test_routes.py  # Route/endpoint tests using Flask test client
    ├── test_startup.py # Startup error handling tests
    └── test_pflanze_inaktiv_properties.py # Property-based tests (Hypothesis)
```

## Architecture Patterns

- Two-file backend: `app.py` (routes + validation) and `db.py` (data access)
- No ORM — raw SQL via `sqlite3`, `sqlite3.Row` for dict-like access
- Schema migrations handled inline in `db.py` `_migrate()` using `PRAGMA table_info` checks
- `init_db()` creates tables + runs migrations on app startup; failure logs a German error and exits
- All DB functions open/close their own connection via `get_db()` (no request-scoped connection)
- Templates extend `base.html`; forms use POST with redirect (PRG pattern)
- Validation constants (valid categories, event types, light levels, etc.) defined at module level in `app.py`
- `_safe_next()` helper for safe redirect targets after form submissions

## Conventions
- German domain terminology throughout code: `ereignis`, `beobachtung`, `pflanze`, `lichtbedarf`, `lebensdauer`, `kategorie`, `phaenologie`
- Route naming follows resource pattern: `/plant/<id>/edit`, `/plant/<id>/ereignis/add`
- Error responses return the same template with an `error` variable and HTTP 400
- Tests use `tmp_path` + `monkeypatch` to isolate the database per test
- `FOREIGN_KEYS = ON` pragma enforced on every connection
