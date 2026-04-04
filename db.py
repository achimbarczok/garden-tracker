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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ereignisse (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            plant_id    INTEGER NOT NULL REFERENCES plants(id) ON DELETE CASCADE,
            ereignistyp TEXT    NOT NULL,
            startmonat  INTEGER NOT NULL,
            endmonat    INTEGER NOT NULL
        )
    """)
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
            "SELECT id, name, type, variety, lichtbedarf, kommentar FROM plants"
        ).fetchall()
        plants = []
        for row in rows:
            plant = dict(row)
            ereignisse = conn.execute(
                "SELECT id, plant_id, ereignistyp, startmonat, endmonat "
                "FROM ereignisse WHERE plant_id = ?",
                (plant["id"],),
            ).fetchall()
            plant["ereignisse"] = [dict(e) for e in ereignisse]
            plants.append(plant)
    return plants


def add_plant(name: str, type: str, variety: str | None,
              lichtbedarf: str, kommentar: str | None) -> None:
    if variety == "":
        variety = None
    if kommentar == "":
        kommentar = None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO plants (name, type, variety, lichtbedarf, kommentar) "
            "VALUES (?, ?, ?, ?, ?)",
            (name, type, variety, lichtbedarf, kommentar),
        )
        conn.commit()


def remove_plant(plant_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
        conn.commit()


def add_ereignis(plant_id: int, ereignistyp: str,
                 startmonat: int, endmonat: int) -> None:
    with get_db() as conn:
        conn.execute(
            "INSERT INTO ereignisse (plant_id, ereignistyp, startmonat, endmonat) "
            "VALUES (?, ?, ?, ?)",
            (plant_id, ereignistyp, startmonat, endmonat),
        )
        conn.commit()


def remove_ereignis(ereignis_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM ereignisse WHERE id = ?", (ereignis_id,))
        conn.commit()


def get_plant(plant_id: int) -> dict | None:
    with get_db() as conn:
        row = conn.execute(
            "SELECT id, name, type, variety, lichtbedarf, kommentar "
            "FROM plants WHERE id = ?",
            (plant_id,),
        ).fetchone()
        if row is None:
            return None
        plant = dict(row)
        ereignisse = conn.execute(
            "SELECT id, plant_id, ereignistyp, startmonat, endmonat "
            "FROM ereignisse WHERE plant_id = ?",
            (plant_id,),
        ).fetchall()
        plant["ereignisse"] = [dict(e) for e in ereignisse]
    return plant


def update_plant(plant_id: int, name: str, type: str, variety: str | None,
                 lichtbedarf: str, kommentar: str | None) -> None:
    if variety == "":
        variety = None
    if kommentar == "":
        kommentar = None
    with get_db() as conn:
        conn.execute(
            "UPDATE plants SET name = ?, type = ?, variety = ?, "
            "lichtbedarf = ?, kommentar = ? WHERE id = ?",
            (name, type, variety, lichtbedarf, kommentar, plant_id),
        )
        conn.commit()
