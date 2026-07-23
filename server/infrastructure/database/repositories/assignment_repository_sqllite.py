"""SQLite adapter for :class:`AssignmentRepository`."""

from __future__ import annotations

import sqlite3

from core.models.assignment import Assignment
from core.repositories.assignment_repository import AssignmentRepository, Key


def _row_to_assignment(row: sqlite3.Row) -> Assignment:
    return Assignment(
        group_id=row["group_id"],
        topic_id=row["topic_id"],
        teacher_id=row["teacher_id"],
        pairs_per_week=row["pairs_per_week"],
    )


class AssignmentRepositorySqlLite(AssignmentRepository):
    """Stores (group, topic) → teacher assignments keyed by group and topic."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def get_all(self) -> dict[Key, Assignment]:
        rows = self._conn.execute("SELECT * FROM assignments").fetchall()
        return {(r["group_id"], r["topic_id"]): _row_to_assignment(r) for r in rows}

    def list_by_year(self, year_id: int) -> dict[Key, Assignment]:
        rows = self._conn.execute(
            """
            SELECT a.* FROM assignments a
            JOIN topics t ON t.id = a.topic_id
            JOIN disciplines d ON d.id = t.discipline_id
            WHERE d.year_id = ?
            """,
            (year_id,),
        ).fetchall()
        return {(r["group_id"], r["topic_id"]): _row_to_assignment(r) for r in rows}

    def list_by_topic(self, topic_id: int) -> list[Assignment]:
        rows = self._conn.execute(
            "SELECT * FROM assignments WHERE topic_id = ?", (topic_id,)
        ).fetchall()
        return [_row_to_assignment(r) for r in rows]

    def get(self, group_id: int, topic_id: int) -> Assignment | None:
        row = self._conn.execute(
            "SELECT * FROM assignments WHERE group_id = ? AND topic_id = ?",
            (group_id, topic_id),
        ).fetchone()
        return _row_to_assignment(row) if row else None

    def set(self, assignment: Assignment) -> None:
        self._conn.execute(
            """
            INSERT INTO assignments (group_id, topic_id, teacher_id, pairs_per_week)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(group_id, topic_id) DO UPDATE SET
                teacher_id = excluded.teacher_id,
                pairs_per_week = excluded.pairs_per_week
            """,
            (
                assignment.group_id,
                assignment.topic_id,
                assignment.teacher_id,
                assignment.pairs_per_week,
            ),
        )
        self._conn.commit()

    def delete(self, group_id: int, topic_id: int) -> None:
        self._conn.execute(
            "DELETE FROM assignments WHERE group_id = ? AND topic_id = ?",
            (group_id, topic_id),
        )
        self._conn.commit()
