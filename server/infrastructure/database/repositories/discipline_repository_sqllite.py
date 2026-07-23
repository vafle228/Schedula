"""SQLite adapters for :class:`DisciplineRepository` and
:class:`TopicRepository`.
"""

from __future__ import annotations

import sqlite3

from core.models.discipline import Discipline, Topic
from core.repositories.discipline_repository import (
    DisciplineRepository,
    TopicRepository,
)


def _row_to_topic(row: sqlite3.Row) -> Topic:
    return Topic(
        id=row["id"],
        discipline_id=row["discipline_id"],
        kind=row["kind"],
        name=row["name"],
        hours=row["hours"],
    )


def _insert_topic(conn: sqlite3.Connection, topic: Topic) -> int:
    cursor = conn.execute(
        "INSERT INTO topics (discipline_id, kind, name, hours) VALUES (?, ?, ?, ?)",
        (topic.discipline_id, topic.kind, topic.name, topic.hours),
    )
    topic.id = cursor.lastrowid
    return topic.id


class DisciplineRepositorySqlLite(DisciplineRepository):
    """Stores disciplines and hydrates their topics on load."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def _topics_for(self, discipline_id: int) -> list[Topic]:
        rows = self._conn.execute(
            "SELECT * FROM topics WHERE discipline_id = ? ORDER BY rowid",
            (discipline_id,),
        ).fetchall()
        return [_row_to_topic(r) for r in rows]

    def _row_to_discipline(self, row: sqlite3.Row) -> Discipline:
        return Discipline(
            id=row["id"],
            name=row["name"],
            group_id=row["group_id"],
            period=row["period"],
            is_new=bool(row["is_new"]),
            topics=self._topics_for(row["id"]),
        )

    def list_all(self) -> list[Discipline]:
        rows = self._conn.execute(
            "SELECT * FROM disciplines ORDER BY rowid"
        ).fetchall()
        return [self._row_to_discipline(r) for r in rows]

    def get(self, discipline_id: int) -> Discipline | None:
        row = self._conn.execute(
            "SELECT * FROM disciplines WHERE id = ?", (discipline_id,)
        ).fetchone()
        return self._row_to_discipline(row) if row else None

    def add(self, discipline: Discipline) -> int:
        cursor = self._conn.execute(
            "INSERT INTO disciplines (name, group_id, period, is_new) VALUES (?, ?, ?, ?)",
            (
                discipline.name,
                discipline.group_id,
                discipline.period,
                int(discipline.is_new),
            ),
        )
        discipline.id = cursor.lastrowid
        for topic in discipline.topics:
            _insert_topic(self._conn, topic)
        self._conn.commit()
        return discipline.id

    def update(self, discipline: Discipline) -> None:
        self._conn.execute(
            "UPDATE disciplines SET name = ?, group_id = ?, period = ?, is_new = ? "
            "WHERE id = ?",
            (
                discipline.name,
                discipline.group_id,
                discipline.period,
                int(discipline.is_new),
                discipline.id,
            ),
        )
        self._conn.commit()

    def delete(self, discipline_id: int) -> None:
        # topics cascade via the FK; assignments cascade off topics in turn
        self._conn.execute("DELETE FROM disciplines WHERE id = ?", (discipline_id,))
        self._conn.commit()


class TopicRepositorySqlLite(TopicRepository):
    """Stores topics of a discipline."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def get(self, topic_id: int) -> Topic | None:
        row = self._conn.execute(
            "SELECT * FROM topics WHERE id = ?", (topic_id,)
        ).fetchone()
        return _row_to_topic(row) if row else None

    def list_by_discipline(self, discipline_id: int) -> list[Topic]:
        rows = self._conn.execute(
            "SELECT * FROM topics WHERE discipline_id = ? ORDER BY rowid",
            (discipline_id,),
        ).fetchall()
        return [_row_to_topic(r) for r in rows]

    def add(self, topic: Topic) -> int:
        result = _insert_topic(self._conn, topic)
        self._conn.commit()
        return result

    def update(self, topic: Topic) -> None:
        self._conn.execute(
            "UPDATE topics SET kind = ?, name = ?, hours = ? WHERE id = ?",
            (topic.kind, topic.name, topic.hours, topic.id),
        )
        self._conn.commit()

    def delete(self, topic_id: int) -> None:
        self._conn.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        self._conn.commit()
