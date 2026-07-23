"""SQLite adapter for :class:`MajorRepository`."""

from __future__ import annotations

import sqlite3

from core.models.major import Major
from core.repositories.major_repository import MajorRepository


def _row_to_major(row: sqlite3.Row) -> Major:
    return Major(id=row["id"], code=row["code"], name=row["name"])


class MajorRepositorySqlLite(MajorRepository):
    """Stores majors, preserving insertion order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[Major]:
        rows = self._conn.execute("SELECT * FROM majors ORDER BY rowid").fetchall()
        return [_row_to_major(r) for r in rows]

    def get(self, major_id: int) -> Major | None:
        row = self._conn.execute(
            "SELECT * FROM majors WHERE id = ?", (major_id,)
        ).fetchone()
        return _row_to_major(row) if row else None

    def add(self, major: Major) -> int:
        cursor = self._conn.execute(
            "INSERT INTO majors (code, name) VALUES (?, ?)",
            (major.code, major.name),
        )
        self._conn.commit()
        major.id = cursor.lastrowid
        return major.id

    def update(self, major: Major) -> None:
        self._conn.execute(
            "UPDATE majors SET code = ?, name = ? WHERE id = ?",
            (major.code, major.name, major.id),
        )
        self._conn.commit()

    def delete(self, major_id: int) -> None:
        self._conn.execute("DELETE FROM majors WHERE id = ?", (major_id,))
        self._conn.commit()
