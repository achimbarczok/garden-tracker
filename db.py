import os
import re
import sqlite3
from pathlib import Path

from flask import g

DB_PATH = os.environ.get("DB_PATH", "/data/plants.db")

_DETAIL_OFFSETS = {"Anfang": 5, "Mitte": 15, "Ende": 25}

# Current schema version — bump when adding migrations
SCHEMA_VERSION = 5


def berechne_sortierwert(monat: int, detail: str | None) -> int:
    """Calculate a numeric sort value from month and optional detail.

    Pure function, no DB access.
    Returns monat * 100 + offset where offset depends on detail:
      "Anfang" → 5, "Mitte" → 15, "Ende" → 25, None/empty → 15
    """
    return monat * 100 + _DETAIL_OFFSETS.get(detail or "", 15)


def get_db() -> sqlite3.Connection:
    """Get a database connection, reusing the Flask request-scoped one if available."""
    try:
        # Inside a Flask request: reuse connection from g
        if "db" not in g:
            conn = sqlite3.connect(DB_PATH)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            g.db = conn
        return g.db
    except RuntimeError:
        # Outside Flask request context (init, tests, scripts): open a fresh connection
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn


def close_db(e=None) -> None:
    """Close the request-scoped database connection if it exists."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def _get_schema_version(conn: sqlite3.Connection) -> int:
    """Read the current schema version from the database (0 if table missing)."""
    try:
        row = conn.execute("SELECT version FROM schema_version").fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0


def _set_schema_version(conn: sqlite3.Connection, version: int) -> None:
    """Store the schema version in the database."""
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
    conn.execute("DELETE FROM schema_version")
    conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))


def _add_column_if_missing(conn: sqlite3.Connection, table: str, column: str, col_type: str) -> None:
    """Add a column to a table if it doesn't already exist."""
    cols = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}")


def _migrate(conn: sqlite3.Connection) -> None:
    current = _get_schema_version(conn)

    if current < 1:
        # V1: plants extras, ereignisse, beobachtungen with detail columns
        for col, col_type in [
            ("lichtbedarf", "TEXT"), ("kommentar", "TEXT"), ("lebensdauer", "TEXT"),
            ("pflanzmonat", "INTEGER"), ("pflanzjahr", "INTEGER"),
            ("anzahl", "INTEGER DEFAULT 1"), ("kategorie", "TEXT"),
            ("beschreibung", "TEXT"), ("farbe", "TEXT"), ("aktiv", "INTEGER DEFAULT 1"),
        ]:
            _add_column_if_missing(conn, "plants", col, col_type)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS ereignisse (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id    INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
                ereignistyp TEXT    NOT NULL,
                startmonat  INTEGER NOT NULL,
                endmonat    INTEGER NOT NULL
            )
        """)
        _add_column_if_missing(conn, "ereignisse", "start_detail", "TEXT")
        _add_column_if_missing(conn, "ereignisse", "end_detail", "TEXT")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS beobachtungen (
                id                  INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id            INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
                jahr                INTEGER NOT NULL,
                ereignistyp         TEXT    NOT NULL,
                startmonat          INTEGER NOT NULL,
                endmonat            INTEGER NOT NULL,
                phaenologische_phase TEXT,
                notiz               TEXT
            )
        """)
        _add_column_if_missing(conn, "beobachtungen", "start_detail", "TEXT")
        _add_column_if_missing(conn, "beobachtungen", "end_detail", "TEXT")

    if current < 2:
        # V2: Phänologie-Tabelle
        conn.execute("""
            CREATE TABLE IF NOT EXISTS phaenologie (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                jahr        INTEGER NOT NULL,
                phase       TEXT    NOT NULL,
                startmonat  INTEGER NOT NULL,
                start_detail TEXT,
                endmonat    INTEGER NOT NULL,
                end_detail  TEXT,
                UNIQUE(jahr, phase)
            )
        """)

    if current < 3:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS fotos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id      INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
                dateiname     TEXT    NOT NULL,
                bezeichnung   TEXT,
                ist_hauptbild INTEGER DEFAULT 0
            )
        """)

    if current < 4:
        # V4: Sträucher + Bäume → Gehölze
        conn.execute("UPDATE plants SET kategorie = 'Gehölze' WHERE kategorie IN ('Sträucher', 'Bäume')")

    if current < 5:
        # V5: Gartenkarte — Kartenbild und Kartenpositionen
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kartenbild (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                dateiname TEXT    NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS kartenpositionen (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                plant_id INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
                x        REAL    NOT NULL,
                y        REAL    NOT NULL
            )
        """)

    _set_schema_version(conn, SCHEMA_VERSION)
    conn.commit()


def generate_satz_name(name: str) -> str:
    """Generate the next 'Satz' name for a duplicated plant.

    Pure function, no DB access.
    - "Tomate" → "Tomate (2. Satz)"
    - "Tomate (2. Satz)" → "Tomate (3. Satz)"
    """
    match = re.match(r'^(.*?)\s*\((\d+)\.\s*Satz\)$', name)
    if match:
        base = match.group(1)
        n = int(match.group(2))
        return f"{base} ({n + 1}. Satz)"
    return f"{name} (2. Satz)"


def duplicate_plant(plant_id: int) -> int:
    """Duplicate a plant with all Stammdaten and Ereignisse.

    Uses an atomic transaction. Beobachtungen are NOT copied.
    Returns the new plant's ID.
    """
    with get_db() as conn:
        # Read source plant
        row = conn.execute(
            "SELECT name, type, variety, lichtbedarf, kommentar, "
            "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, "
            "beschreibung, farbe, aktiv FROM plants WHERE id = ?",
            (plant_id,),
        ).fetchone()
        if row is None:
            raise ValueError(f"Pflanze mit ID {plant_id} nicht gefunden")
        plant = dict(row)

        # Generate new name
        new_name = generate_satz_name(plant["name"])

        # Insert new plant with all Stammdaten, always aktiv = 1
        cursor = conn.execute(
            "INSERT INTO plants (name, type, variety, lichtbedarf, kommentar, "
            "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, "
            "beschreibung, farbe, aktiv) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)",
            (new_name, plant["type"], plant["variety"], plant["lichtbedarf"],
             plant["kommentar"], plant["lebensdauer"], plant["pflanzmonat"],
             plant["pflanzjahr"], plant["anzahl"], plant["kategorie"],
             plant["beschreibung"], plant["farbe"]),
        )
        new_id = cursor.lastrowid

        # Copy all Ereignisse with new plant_id
        ereignisse = conn.execute(
            "SELECT ereignistyp, startmonat, endmonat, start_detail, end_detail "
            "FROM ereignisse WHERE plant_id = ?",
            (plant_id,),
        ).fetchall()
        for e in ereignisse:
            conn.execute(
                "INSERT INTO ereignisse (plant_id, ereignistyp, startmonat, "
                "endmonat, start_detail, end_detail) VALUES (?, ?, ?, ?, ?, ?)",
                (new_id, e["ereignistyp"], e["startmonat"], e["endmonat"],
                 e["start_detail"], e["end_detail"]),
            )

        conn.commit()
    return new_id


def set_plant_active(plant_id: int, aktiv: int) -> None:
    with get_db() as conn:
        conn.execute("UPDATE plants SET aktiv = ? WHERE id = ?", (aktiv, plant_id))
        conn.commit()


def _raw_connection() -> sqlite3.Connection:
    """Open a raw connection (bypasses Flask g). Used for init/scripts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _raw_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS plants (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                type    TEXT    NOT NULL,
                variety TEXT
            )
            """
        )
        conn.commit()
        _migrate(conn)


def get_all_plants(include_inactive: bool = False) -> list[dict]:
    with get_db() as conn:
        if include_inactive:
            rows = conn.execute(
                "SELECT id, name, type, variety, lichtbedarf, kommentar, "
                "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, "
                "beschreibung, farbe, aktiv FROM plants "
                "ORDER BY name COLLATE NOCASE"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, name, type, variety, lichtbedarf, kommentar, "
                "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, "
                "beschreibung, farbe, aktiv FROM plants WHERE aktiv = 1 "
                "ORDER BY name COLLATE NOCASE"
            ).fetchall()
        plants = []
        for row in rows:
            plant = dict(row)
            ereignisse = conn.execute(
                "SELECT id, plant_id, ereignistyp, startmonat, endmonat, "
                "start_detail, end_detail "
                "FROM ereignisse WHERE plant_id = ?",
                (plant["id"],),
            ).fetchall()
            plant["ereignisse"] = [dict(e) for e in ereignisse]
            plants.append(plant)
    return plants


def get_all_beobachtungen() -> list[dict]:
    """Get all observations joined with active plants, sorted by sortierwert and name."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT b.id AS beobachtung_id, b.plant_id, p.name AS plant_name, "
            "p.kategorie, b.jahr, b.ereignistyp, "
            "b.startmonat, b.endmonat, b.start_detail, b.end_detail, b.notiz, "
            "(b.startmonat * 100 + CASE b.start_detail "
            "WHEN 'Anfang' THEN 5 WHEN 'Ende' THEN 25 ELSE 15 "
            "END) AS sortierwert "
            "FROM beobachtungen b "
            "JOIN plants p ON b.plant_id = p.id "
            "WHERE p.aktiv = 1 "
            "ORDER BY sortierwert ASC, p.name ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def get_all_ereignisse() -> list[dict]:
    """Get all events joined with active plants, sorted by sortierwert and name."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT e.id AS ereignis_id, e.plant_id, p.name AS plant_name, "
            "p.kategorie, e.ereignistyp, "
            "e.startmonat, e.endmonat, e.start_detail, e.end_detail, "
            "(e.startmonat * 100 + CASE e.start_detail "
            "WHEN 'Anfang' THEN 5 WHEN 'Ende' THEN 25 ELSE 15 "
            "END) AS sortierwert "
            "FROM ereignisse e "
            "JOIN plants p ON e.plant_id = p.id "
            "WHERE p.aktiv = 1 "
            "ORDER BY sortierwert ASC, p.name ASC"
        ).fetchall()
    return [dict(r) for r in rows]


def add_plant(name: str, type: str, variety: str | None,
              lichtbedarf: str, kommentar: str | None,
              lebensdauer: str | None = None,
              pflanzmonat: int | None = None,
              pflanzjahr: int | None = None,
              anzahl: int = 1,
              kategorie: str | None = None,
              beschreibung: str | None = None,
              farbe: str | None = None) -> None:
    if variety == "":
        variety = None
    if kommentar == "":
        kommentar = None
    if beschreibung == "":
        beschreibung = None
    if type is None:
        type = ""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO plants (name, type, variety, lichtbedarf, kommentar, "
            "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, beschreibung, farbe) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (name, type, variety, lichtbedarf, kommentar,
             lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, beschreibung, farbe),
        )
        conn.commit()


def remove_plant(plant_id: int) -> None:
    fotos_dir = Path(DB_PATH).parent / "fotos"
    dateinamen = get_fotos_by_plant_id(plant_id)
    with get_db() as conn:
        conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
        conn.commit()
    for name in dateinamen:
        try:
            (fotos_dir / name).unlink()
        except OSError:
            pass


def add_ereignis(plant_id: int, ereignistyp: str,
                 startmonat: int, endmonat: int,
                 start_detail: str | None = None,
                 end_detail: str | None = None) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO ereignisse (plant_id, ereignistyp, startmonat, endmonat, "
            "start_detail, end_detail) VALUES (?, ?, ?, ?, ?, ?)",
            (plant_id, ereignistyp, startmonat, endmonat, start_detail, end_detail),
        )
        conn.commit()


def remove_ereignis(ereignis_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM ereignisse WHERE id = ?", (ereignis_id,))
        conn.commit()


def update_ereignis(ereignis_id: int, ereignistyp: str,
                    startmonat: int, endmonat: int,
                    start_detail: str | None = None,
                    end_detail: str | None = None) -> None:
    with get_db() as conn:
        conn.execute(
            "UPDATE ereignisse SET ereignistyp = ?, startmonat = ?, endmonat = ?, "
            "start_detail = ?, end_detail = ? WHERE id = ?",
            (ereignistyp, startmonat, endmonat, start_detail, end_detail, ereignis_id),
        )
        conn.commit()


def get_plant(plant_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, name, type, variety, lichtbedarf, kommentar, "
            "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, "
            "beschreibung, farbe, aktiv "
            "FROM plants WHERE id = ?",
            (plant_id,),
        ).fetchone()
        if row is None:
            return None
        plant = dict(row)
        ereignisse = conn.execute(
            "SELECT id, plant_id, ereignistyp, startmonat, endmonat, "
            "start_detail, end_detail "
            "FROM ereignisse WHERE plant_id = ?",
            (plant_id,),
        ).fetchall()
        plant["ereignisse"] = [dict(e) for e in ereignisse]
        beobachtungen = conn.execute(
            "SELECT id, plant_id, jahr, ereignistyp, startmonat, endmonat, "
            "phaenologische_phase, notiz, start_detail, end_detail "
            "FROM beobachtungen WHERE plant_id = ? ORDER BY jahr DESC, startmonat",
            (plant_id,),
        ).fetchall()
        plant["beobachtungen"] = [dict(b) for b in beobachtungen]
        plant["fotos"] = get_fotos(plant_id)
    return plant


def update_plant(plant_id: int, name: str, type: str, variety: str | None,
                 lichtbedarf: str, kommentar: str | None,
                 lebensdauer: str | None = None,
                 pflanzmonat: int | None = None,
                 pflanzjahr: int | None = None,
                 anzahl: int = 1,
                 kategorie: str | None = None,
                 beschreibung: str | None = None,
                 farbe: str | None = None) -> None:
    if variety == "":
        variety = None
    if kommentar == "":
        kommentar = None
    if beschreibung == "":
        beschreibung = None
    if type is None:
        type = ""
    with get_db() as conn:
        conn.execute(
            "UPDATE plants SET name = ?, type = ?, variety = ?, "
            "lichtbedarf = ?, kommentar = ?, lebensdauer = ?, "
            "pflanzmonat = ?, pflanzjahr = ?, anzahl = ?, kategorie = ?, "
            "beschreibung = ?, farbe = ? WHERE id = ?",
            (name, type, variety, lichtbedarf, kommentar,
             lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie,
             beschreibung, farbe, plant_id),
        )
        conn.commit()


def add_beobachtung(plant_id: int, jahr: int, ereignistyp: str,
                    startmonat: int, endmonat: int,
                    phaenologische_phase: str | None = None,
                    notiz: str | None = None,
                    start_detail: str | None = None,
                    end_detail: str | None = None) -> None:
    if phaenologische_phase == "":
        phaenologische_phase = None
    if notiz == "":
        notiz = None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO beobachtungen "
            "(plant_id, jahr, ereignistyp, startmonat, endmonat, "
            "phaenologische_phase, notiz, start_detail, end_detail) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (plant_id, jahr, ereignistyp, startmonat, endmonat,
             phaenologische_phase, notiz, start_detail, end_detail),
        )
        conn.commit()


def remove_beobachtung(beobachtung_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM beobachtungen WHERE id = ?", (beobachtung_id,))
        conn.commit()


def update_beobachtung(beobachtung_id: int, jahr: int, ereignistyp: str,
                       startmonat: int, endmonat: int,
                       phaenologische_phase: str | None = None,
                       notiz: str | None = None,
                       start_detail: str | None = None,
                       end_detail: str | None = None) -> None:
    if phaenologische_phase == "":
        phaenologische_phase = None
    if notiz == "":
        notiz = None
    with get_db() as conn:
        conn.execute(
            "UPDATE beobachtungen SET jahr = ?, ereignistyp = ?, startmonat = ?, "
            "endmonat = ?, phaenologische_phase = ?, notiz = ?, "
            "start_detail = ?, end_detail = ? WHERE id = ?",
            (jahr, ereignistyp, startmonat, endmonat,
             phaenologische_phase, notiz, start_detail, end_detail, beobachtung_id),
        )
        conn.commit()


def get_fotos(plant_id: int) -> list[dict]:
    """Get all fotos for a plant, sorted by id."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, plant_id, dateiname, bezeichnung, ist_hauptbild "
            "FROM fotos WHERE plant_id = ? ORDER BY id",
            (plant_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def count_fotos(plant_id: int) -> int:
    """Count fotos for a plant."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT COUNT(*) FROM fotos WHERE plant_id = ?",
            (plant_id,),
        ).fetchone()
    return row[0]


def add_foto(plant_id: int, dateiname: str, bezeichnung: str | None,
             ist_hauptbild: int = 0) -> int:
    """Insert a foto and return the new id.

    If ist_hauptbild=1, first set all other fotos of the plant to 0.
    """
    with get_db() as conn:
        if ist_hauptbild:
            conn.execute(
                "UPDATE fotos SET ist_hauptbild = 0 WHERE plant_id = ?",
                (plant_id,),
            )
        cursor = conn.execute(
            "INSERT INTO fotos (plant_id, dateiname, bezeichnung, ist_hauptbild) "
            "VALUES (?, ?, ?, ?)",
            (plant_id, dateiname, bezeichnung, ist_hauptbild),
        )
        conn.commit()
    return cursor.lastrowid


def get_foto(foto_id: int) -> dict | None:
    """Get a single foto by id."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, plant_id, dateiname, bezeichnung, ist_hauptbild "
            "FROM fotos WHERE id = ?",
            (foto_id,),
        ).fetchone()
    return dict(row) if row else None


def remove_foto(foto_id: int) -> None:
    """Delete a foto by id."""
    with get_db() as conn:
        conn.execute("DELETE FROM fotos WHERE id = ?", (foto_id,))
        conn.commit()


def set_hauptbild(foto_id: int, plant_id: int) -> None:
    """Atomic update: set all fotos of plant to ist_hauptbild=0, then set the chosen one to 1."""
    with get_db() as conn:
        conn.execute(
            "UPDATE fotos SET ist_hauptbild = 0 WHERE plant_id = ?",
            (plant_id,),
        )
        conn.execute(
            "UPDATE fotos SET ist_hauptbild = 1 WHERE id = ?",
            (foto_id,),
        )
        conn.commit()


def get_fotos_by_plant_id(plant_id: int) -> list[str]:
    """Return list of dateiname strings for a plant (used when deleting a plant)."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT dateiname FROM fotos WHERE plant_id = ?",
            (plant_id,),
        ).fetchall()
    return [r[0] for r in rows]


def get_kartenbild() -> dict | None:
    """Get the single garden map image entry, or None."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, dateiname FROM kartenbild LIMIT 1"
        ).fetchone()
    return dict(row) if row else None


def save_kartenbild(dateiname: str) -> None:
    """Replace the garden map image (max 1 row)."""
    with get_db() as conn:
        conn.execute("DELETE FROM kartenbild")
        conn.execute(
            "INSERT INTO kartenbild (dateiname) VALUES (?)",
            (dateiname,),
        )
        conn.commit()


def remove_kartenbild() -> None:
    """Delete the garden map image and all positions (atomic)."""
    with get_db() as conn:
        conn.execute("DELETE FROM kartenpositionen")
        conn.execute("DELETE FROM kartenbild")
        conn.commit()


def get_kartenpositionen() -> list[dict]:
    """Get all map positions with plant name and color."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT kp.id, kp.plant_id, kp.x, kp.y, p.name, p.farbe "
            "FROM kartenpositionen kp "
            "JOIN plants p ON kp.plant_id = p.id "
            "ORDER BY kp.id"
        ).fetchall()
    return [dict(r) for r in rows]


def add_kartenposition(plant_id: int, x: float, y: float) -> None:
    """Add a plant position on the garden map."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO kartenpositionen (plant_id, x, y) VALUES (?, ?, ?)",
            (plant_id, x, y),
        )
        conn.commit()


def remove_kartenposition(position_id: int) -> None:
    """Remove a single map position."""
    with get_db() as conn:
        conn.execute("DELETE FROM kartenpositionen WHERE id = ?", (position_id,))
        conn.commit()


PHAENOLOGISCHE_PHASEN = [
    "Vorfrühling", "Erstfrühling", "Vollfrühling",
    "Frühsommer", "Hochsommer", "Spätsommer",
    "Frühherbst", "Vollherbst", "Spätherbst",
    "Winter",
]

PHASEN_ICONS = {
    "Vorfrühling": "🌱",
    "Erstfrühling": "🌼",
    "Vollfrühling": "🌸",
    "Frühsommer": "☀️",
    "Hochsommer": "🌻",
    "Spätsommer": "🍎",
    "Frühherbst": "🍇",
    "Vollherbst": "🍂",
    "Spätherbst": "🍁",
    "Winter": "❄️",
}


def get_phaenologie_jahr(jahr: int) -> list[dict]:
    """Get all phenology entries for a given year, ordered by phase."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, jahr, phase, startmonat, start_detail, endmonat, end_detail "
            "FROM phaenologie WHERE jahr = ? ORDER BY id",
            (jahr,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_phaenologie_alle_jahre() -> list[int]:
    """Get all years that have phenology data."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT DISTINCT jahr FROM phaenologie ORDER BY jahr DESC"
        ).fetchall()
    return [r[0] for r in rows]


def upsert_phaenologie(jahr: int, phase: str, startmonat: int,
                       start_detail: str | None) -> None:
    """Insert or update a phenology entry (only start; end is implicit from next phase)."""
    with get_db() as conn:
        existing = conn.execute(
            "SELECT id FROM phaenologie WHERE jahr = ? AND phase = ?",
            (jahr, phase),
        ).fetchone()
        if existing:
            conn.execute(
                "UPDATE phaenologie SET startmonat = ?, start_detail = ? WHERE id = ?",
                (startmonat, start_detail, existing[0]),
            )
        else:
            conn.execute(
                "INSERT INTO phaenologie (jahr, phase, startmonat, start_detail, "
                "endmonat, end_detail) VALUES (?, ?, ?, ?, ?, ?)",
                (jahr, phase, startmonat, start_detail, startmonat, start_detail),
            )
        conn.commit()


def remove_phaenologie(phaenologie_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM phaenologie WHERE id = ?", (phaenologie_id,))
        conn.commit()


def get_aktuelle_phase(heute_monat: int, heute_tag: int, jahr: int) -> str | None:
    """Determine the current phenological phase based on today's date.

    Each phase lasts from its own start until the start of the next phase.
    The last recorded phase extends to the end of the year.
    """
    phasen = get_phaenologie_jahr(jahr)
    if not phasen:
        return None

    def to_day(detail):
        if detail == "Anfang": return 5
        if detail == "Mitte": return 15
        if detail == "Ende": return 25
        return 1

    heute_val = heute_monat * 100 + heute_tag

    # Sort by start value
    sorted_phasen = sorted(phasen, key=lambda p: p["startmonat"] * 100 + to_day(p.get("start_detail")))

    for i, p in enumerate(sorted_phasen):
        start_val = p["startmonat"] * 100 + to_day(p.get("start_detail"))
        if i + 1 < len(sorted_phasen):
            next_start = sorted_phasen[i + 1]["startmonat"] * 100 + to_day(sorted_phasen[i + 1].get("start_detail"))
            end_val = next_start - 1
        else:
            end_val = 1231  # end of year
        if start_val <= heute_val <= end_val:
            return p["phase"]
    return None
