import os
import sqlite3

DB_PATH = os.environ.get("DB_PATH", "/data/plants.db")


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


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


def get_all_plants() -> list[dict]:
    with get_db() as conn:
        rows = conn.execute("SELECT id, name, type, variety FROM plants").fetchall()
    return [dict(row) for row in rows]


def add_plant(name: str, type: str, variety: str | None) -> None:
    if variety == "":
        variety = None
    with get_db() as conn:
        conn.execute(
            "INSERT INTO plants (name, type, variety) VALUES (?, ?, ?)",
            (name, type, variety),
        )
        conn.commit()


def remove_plant(plant_id: int) -> None:
    with get_db() as conn:
        conn.execute("DELETE FROM plants WHERE id = ?", (plant_id,))
        conn.commit()
