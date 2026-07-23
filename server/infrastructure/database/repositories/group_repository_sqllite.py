"""SQLite adapter for :class:`GroupRepository`."""

from __future__ import annotations

import sqlite3

from core.models.group import Group
from core.repositories.group_repository import GroupRepository


def _row_to_group(row: sqlite3.Row) -> Group:
    return Group(
        id=row["id"],
        year_id=row["year_id"],
        name=row["name"],
        major_id=row["major_id"],
        course=row["course"],
    )


class GroupRepositorySqlLite(GroupRepository):
    """Stores year-scoped groups, preserving insertion order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[Group]:
        rows = self._conn.execute("SELECT * FROM groups ORDER BY rowid").fetchall()
        return [_row_to_group(r) for r in rows]

    def list_by_year(self, year_id: int) -> list[Group]:
        rows = self._conn.execute(
            "SELECT * FROM groups WHERE year_id = ? ORDER BY rowid", (year_id,)
        ).fetchall()
        return [_row_to_group(r) for r in rows]

    def list_by_year_major(self, year_id: int, major_id: int) -> list[Group]:
        rows = self._conn.execute(
            "SELECT * FROM groups WHERE year_id = ? AND major_id = ? ORDER BY rowid",
            (year_id, major_id),
        ).fetchall()
        return [_row_to_group(r) for r in rows]

    def get(self, group_id: int) -> Group | None:
        row = self._conn.execute(
            "SELECT * FROM groups WHERE id = ?", (group_id,)
        ).fetchone()
        return _row_to_group(row) if row else None

    def add(self, group: Group) -> int:
        cursor = self._conn.execute(
            "INSERT INTO groups (year_id, name, major_id, course) VALUES (?, ?, ?, ?)",
            (group.year_id, group.name, group.major_id, group.course),
        )
        self._conn.commit()
        group.id = cursor.lastrowid
        return group.id

    def update(self, group: Group) -> None:
        self._conn.execute(
            "UPDATE groups SET name = ?, major_id = ?, course = ? WHERE id = ?",
            (group.name, group.major_id, group.course, group.id),
        )
        self._conn.commit()

    def delete(self, group_id: int) -> None:
        self._conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        self._conn.commit()
