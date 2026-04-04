import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "/data/plants.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _migrate(conn: sqlite3.Connection) -> None:
    cols = {row[1] for row in conn.execute("PRAGMA table_info(plants)")}
    if "lichtbedarf" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN lichtbedarf TEXT")
    if "kommentar" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN kommentar TEXT")
    if "lebensdauer" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN lebensdauer TEXT")
    if "pflanzmonat" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN pflanzmonat INTEGER")
    if "pflanzjahr" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN pflanzjahr INTEGER")
    if "anzahl" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN anzahl INTEGER DEFAULT 1")
    if "kategorie" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN kategorie TEXT")
    if "beschreibung" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN beschreibung TEXT")
    if "farbe" not in cols:
        conn.execute("ALTER TABLE plants ADD COLUMN farbe TEXT")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ereignisse (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id    INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
            ereignistyp TEXT    NOT NULL,
            startmonat  INTEGER NOT NULL,
            endmonat    INTEGER NOT NULL
        )
    """)
    # Migration: start_detail/end_detail für ereignisse
    ecols = {row[1] for row in conn.execute("PRAGMA table_info(ereignisse)")}
    if "start_detail" not in ecols:
        conn.execute("ALTER TABLE ereignisse ADD COLUMN start_detail TEXT")
    if "end_detail" not in ecols:
        conn.execute("ALTER TABLE ereignisse ADD COLUMN end_detail TEXT")
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
    # Migration: start_detail/end_detail für beobachtungen
    bcols = {row[1] for row in conn.execute("PRAGMA table_info(beobachtungen)")}
    if "start_detail" not in bcols:
        conn.execute("ALTER TABLE beobachtungen ADD COLUMN start_detail TEXT")
    if "end_detail" not in bcols:
        conn.execute("ALTER TABLE beobachtungen ADD COLUMN end_detail TEXT")
    conn.commit()


def init_db() -> None:
    with get_db() as conn:
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


def get_all_plants() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, name, type, variety, lichtbedarf, kommentar, "
            "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, beschreibung, farbe FROM plants"
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
    if type == "":
        type = None
    if beschreibung == "":
        beschreibung = None
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
    with get_db() as conn:
        conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
        conn.commit()


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


def get_plant(plant_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, name, type, variety, lichtbedarf, kommentar, "
            "lebensdauer, pflanzmonat, pflanzjahr, anzahl, kategorie, beschreibung, farbe "
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
    if type == "":
        type = None
    if beschreibung == "":
        beschreibung = None
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
