"""SQLite adapter for :class:`AssignmentRepository`."""

from __future__ import annotations

import sqlite3

from core.models.assignment import Assignment
from core.repositories.assignment_repository import AssignmentRepository


def _row_to_assignment(row: sqlite3.Row) -> Assignment:
    return Assignment(
        topic_id=row["topic_id"],
        teacher_id=row["teacher_id"],
        pairs_per_week=row["pairs_per_week"],
    )


class AssignmentRepositorySqlLite(AssignmentRepository):
    """Stores topic → teacher assignments keyed by topic."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def get_all(self) -> dict[int, Assignment]:
        rows = self._conn.execute("SELECT * FROM assignments").fetchall()
        return {r["topic_id"]: _row_to_assignment(r) for r in rows}

    def get(self, topic_id: int) -> Assignment | None:
        row = self._conn.execute(
            "SELECT * FROM assignments WHERE topic_id = ?", (topic_id,)
        ).fetchone()
        return _row_to_assignment(row) if row else None

    def set(self, assignment: Assignment) -> None:
        self._conn.execute(
            """
            INSERT INTO assignments (topic_id, teacher_id, pairs_per_week)
            VALUES (?, ?, ?)
            ON CONFLICT(topic_id) DO UPDATE SET
                teacher_id = excluded.teacher_id,
                pairs_per_week = excluded.pairs_per_week
            """,
            (assignment.topic_id, assignment.teacher_id, assignment.pairs_per_week),
        )
        self._conn.commit()

    def delete(self, topic_id: int) -> None:
        self._conn.execute("DELETE FROM assignments WHERE topic_id = ?", (topic_id,))
        self._conn.commit()
