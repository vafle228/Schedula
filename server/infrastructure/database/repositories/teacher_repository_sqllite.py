"""SQLite adapter for :class:`TeacherRepository`.

Constraints ride along as a JSON column on the teacher row; absences live in
their own table and are hydrated on load.
"""

from __future__ import annotations

import json
import sqlite3

from core.models.teacher import Absence, AbsenceType, Teacher, TeacherConstraints
from core.repositories.teacher_repository import TeacherRepository


def _constraints_to_json(c: TeacherConstraints | None) -> str | None:
    if c is None:
        return None
    return json.dumps(
        {"hard": c.hard, "soft": c.soft, "method": c.method, "max_per_day": c.max_per_day}
    )


def _constraints_from_json(raw: str | None) -> TeacherConstraints | None:
    if not raw:
        return None
    data = json.loads(raw)
    return TeacherConstraints(
        hard=data.get("hard", []),
        soft=data.get("soft", []),
        method=data.get("method"),
        max_per_day=data.get("max_per_day"),
    )


def _row_to_absence(row: sqlite3.Row) -> Absence:
    return Absence(
        id=row["id"],
        teacher_id=row["teacher_id"],
        type=AbsenceType(row["type"]),
        label=row["label"],
    )


class TeacherRepositorySqlLite(TeacherRepository):
    """Stores teachers with embedded constraints and hydrated absences."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def _absences_for(self, teacher_id: int) -> list[Absence]:
        rows = self._conn.execute(
            "SELECT * FROM absences WHERE teacher_id = ? ORDER BY rowid",
            (teacher_id,),
        ).fetchall()
        return [_row_to_absence(r) for r in rows]

    def _row_to_teacher(self, row: sqlite3.Row) -> Teacher:
        return Teacher(
            id=row["id"],
            name=row["name"],
            photo=row["photo"],
            constraints=_constraints_from_json(row["constraints"]),
            absences=self._absences_for(row["id"]),
        )

    def list_all(self) -> list[Teacher]:
        rows = self._conn.execute("SELECT * FROM teachers ORDER BY rowid").fetchall()
        return [self._row_to_teacher(r) for r in rows]

    def get(self, teacher_id: int) -> Teacher | None:
        row = self._conn.execute(
            "SELECT * FROM teachers WHERE id = ?", (teacher_id,)
        ).fetchone()
        return self._row_to_teacher(row) if row else None

    def add(self, teacher: Teacher) -> int:
        cursor = self._conn.execute(
            "INSERT INTO teachers (name, photo, constraints) VALUES (?, ?, ?)",
            (
                teacher.name,
                teacher.photo,
                _constraints_to_json(teacher.constraints),
            ),
        )
        self._conn.commit()
        teacher.id = cursor.lastrowid
        return teacher.id

    def update(self, teacher: Teacher) -> None:
        self._conn.execute(
            "UPDATE teachers SET name = ?, photo = ?, constraints = ? WHERE id = ?",
            (
                teacher.name,
                teacher.photo,
                _constraints_to_json(teacher.constraints),
                teacher.id,
            ),
        )
        self._conn.commit()

    def delete(self, teacher_id: int) -> None:
        self._conn.execute("DELETE FROM teachers WHERE id = ?", (teacher_id,))
        self._conn.commit()
