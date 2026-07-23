"""SQLite adapter for :class:`AbsenceRepository`."""

from __future__ import annotations

import sqlite3

from core.models.teacher import Absence
from core.repositories.absence_repository import AbsenceRepository
from infrastructure.database.repositories.teacher_repository_sqllite import (
    _row_to_absence,
)


class AbsenceRepositorySqlLite(AbsenceRepository):
    """Stores teacher absences, preserving order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_for_teacher(self, teacher_id: int) -> list[Absence]:
        rows = self._conn.execute(
            "SELECT * FROM absences WHERE teacher_id = ? ORDER BY rowid",
            (teacher_id,),
        ).fetchall()
        return [_row_to_absence(r) for r in rows]

    def get(self, absence_id: int) -> Absence | None:
        row = self._conn.execute(
            "SELECT * FROM absences WHERE id = ?", (absence_id,)
        ).fetchone()
        return _row_to_absence(row) if row else None

    def add(self, absence: Absence) -> int:
        cursor = self._conn.execute(
            "INSERT INTO absences (teacher_id, type, label) VALUES (?, ?, ?)",
            (absence.teacher_id, str(absence.type), absence.label),
        )
        self._conn.commit()
        absence.id = cursor.lastrowid
        return absence.id

    def update(self, absence: Absence) -> None:
        self._conn.execute(
            "UPDATE absences SET type = ?, label = ? WHERE id = ?",
            (str(absence.type), absence.label, absence.id),
        )
        self._conn.commit()

    def delete(self, absence_id: int) -> None:
        self._conn.execute("DELETE FROM absences WHERE id = ?", (absence_id,))
        self._conn.commit()
