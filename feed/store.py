"""Store: the SQLite file. The registry is data; its sources are copied into the database."""

import sqlite3
from pathlib import Path

_SCHEMA = Path(__file__).with_name("schema.sql")
_SOURCE_FIELDS = (
    "id",
    "name",
    "url",
    "access_path",
    "owner_rank",
    "place",
    "default_town",
    "default_category",
)


def open_db(path: str, registry: dict) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(_SCHEMA.read_text(encoding="utf-8"))
    for source in registry["sources"]:
        towns = registry["places"][source["place"]]["towns"]
        if source.get("default_town") and source["default_town"] not in towns:
            raise ValueError(f"{source['id']}: default town is not a town of its place")
        db.execute(
            f"INSERT OR REPLACE INTO source ({', '.join(_SOURCE_FIELDS)}) "
            f"VALUES ({', '.join('?' * len(_SOURCE_FIELDS))})",
            [source.get(field) for field in _SOURCE_FIELDS],
        )
    db.commit()
    return db
