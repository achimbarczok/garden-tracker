# Implementation Plan: Garden Tracker

## Overview

Implement a minimal Flask + SQLite garden tracking web app with a German UI, packaged as a Docker container for linux/arm64 (Raspberry Pi). Tasks follow the design in `design.md` and cover the database layer, Flask routes, Jinja2 templates, Docker packaging, and a Raspberry Pi deployment README.

## Tasks

- [x] 1. Project structure and configuration
  - Create directory layout: `app.py`, `db.py`, `templates/`, `static/`, `tests/`, `Dockerfile`, `requirements.txt`
  - Add `requirements.txt` with `flask` and `hypothesis` (for property tests)
  - Define `DB_PATH` and `PORT` from environment variables with sensible defaults (`/data/plants.db`, `5000`)
  - _Requirements: 2.2, 2.3_

- [x] 2. Database layer (`db.py`)
  - [x] 2.1 Implement `get_db()`, `init_db()`, `get_all_plants()`, `add_plant()`, `remove_plant()` as specified in the design
    - `init_db()` creates the `plants` table if it does not exist
    - `add_plant()` normalises empty variety string to `None`
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 2.3_
  - [ ]* 2.2 Write property test: round-trip add/retrieve (Property 1)
    - **Property 1: Pflanze hinzufügen und abrufen (Round-Trip)**
    - **Validates: Requirements 1.1, 1.3, 1.5**
    - Use Hypothesis to generate random valid plant dicts; insert all, assert all present in `get_all_plants()` with identical field values
  - [ ]* 2.3 Write property test: remove plant (Property 2)
    - **Property 2: Pflanze entfernen**
    - **Validates: Requirements 1.4**
    - Insert a random plant, call `remove_plant(id)`, assert it is absent from `get_all_plants()` while all other plants remain
  - [ ]* 2.4 Write property test: German characters round-trip (Property 4)
    - **Property 4: Deutsche Sonderzeichen werden korrekt gespeichert und angezeigt**
    - **Validates: Requirements 3.3**
    - Generate strings containing ä, ö, ü, ß, Ä, Ö, Ü; store and retrieve, assert byte-for-byte equality

- [x] 3. Startup error handling
  - In `app.py` (or a startup helper), wrap `get_db()` / `init_db()` in a try/except at import time
  - Log a descriptive German error message and call `sys.exit(1)` if the database is unreachable
  - _Requirements: 2.4_
  - [ ]* 3.1 Write unit test: startup fails on bad DB path (`test_startup_fails_on_bad_db`)
    - Point `DB_PATH` at an unwritable location, assert process exits with non-zero code and logs an error
    - _Requirements: 2.4_

- [x] 4. Flask routes (`app.py`)
  - [x] 4.1 Implement `GET /` — fetch all plants, render `index.html`
    - _Requirements: 1.1, 1.2_
  - [x] 4.2 Implement `POST /add` — validate `name` and `type` (non-empty, non-whitespace); return HTTP 400 with German error message on failure; redirect to `/` on success
    - _Requirements: 1.3, 3.1, 3.2_
  - [x] 4.3 Implement `POST /remove/<int:id>` — call `remove_plant(id)`; return HTTP 404 for unknown id or silently ignore; redirect to `/`
    - _Requirements: 1.4_
  - [ ]* 4.4 Write unit test: empty state message (`test_empty_state_message`)
    - Empty DB → GET `/` returns 200 with German empty-state text
    - _Requirements: 1.6, 3.2_
  - [ ]* 4.5 Write unit test: German error messages (`test_german_error_messages`)
    - POST `/add` with blank name → HTTP 400 response contains German error text
    - _Requirements: 3.1, 3.2_

- [x] 5. Jinja2 templates and CSS
  - [x] 5.1 Create `templates/base.html` with `<html lang="de">`, German page title, and CSS link
    - _Requirements: 3.1_
  - [x] 5.2 Create `templates/index.html` extending `base.html`
    - Plant list table showing name, type, variety (if set) for each plant
    - German empty-state message when no plants exist
    - Add-plant form with German labels (Name, Typ, Sorte) and submit button
    - Remove button per plant row (POST form)
    - _Requirements: 1.1, 1.2, 1.6, 3.1_
  - [x] 5.3 Create `static/style.css` with minimal readable styles
  - [ ]* 5.4 Write property test: rendered HTML contains all plant fields (Property 3)
    - **Property 3: Pflanzenliste rendert alle Felder**
    - **Validates: Requirements 1.2**
    - Use Hypothesis to generate random plant records; render `index.html` via Flask test client; assert name, type, and variety (when set) appear in the HTML

- [x] 6. Checkpoint — ensure all tests pass
  - Run `pytest tests/ --tb=short`; fix any failures before continuing
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Docker packaging
  - [x] 7.1 Write `Dockerfile`
    - Base image: `python:3.12-slim`
    - `--platform linux/arm64` target
    - Copy source, install dependencies from `requirements.txt`
    - Add a non-root `USER` directive (e.g., `appuser`)
    - Expose configurable port via `ENV PORT=5000` and `EXPOSE $PORT`
    - Set `VOLUME ["/data"]` and default `ENV DB_PATH=/data/plants.db`
    - Entrypoint: `flask run --host=0.0.0.0 --port=$PORT`
    - _Requirements: 2.1, 2.2, 2.3, 2.5_
  - [ ]* 7.2 Smoke-test Dockerfile structure
    - Verify `--platform linux/arm64` directive is present
    - Verify a non-root `USER` directive is present
    - _Requirements: 2.1, 2.5_

- [x] 8. Raspberry Pi deployment README
  - Create `README.md` at the project root covering:
    - Prerequisites (Docker with buildx, Git)
    - Cloning the repository: `git clone <repo-url>`
    - Building the image for linux/arm64: `docker buildx build --platform linux/arm64 -t garden-tracker .`
    - Running the container with a volume mount and configurable port:
      `docker run -d -p <HOST_PORT>:5000 -v garden-data:/data --name garden-tracker garden-tracker`
    - How to change the port via the `PORT` environment variable
    - How to stop and remove the container
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 9. Final checkpoint — ensure all tests pass
  - Run `pytest tests/ --tb=short`; confirm all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Property tests use [Hypothesis](https://hypothesis.readthedocs.io/) with at least 100 iterations per property
- All user-facing text (labels, messages, errors) must be in German
- The README (task 8) is a coding/documentation artifact and is part of the deployable repository
