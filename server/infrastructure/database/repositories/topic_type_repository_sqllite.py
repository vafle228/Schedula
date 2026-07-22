"""SQLite adapter for :class:`TopicTypeRepository`."""

from __future__ import annotations

import sqlite3

from core.models.topic_type import TopicType
from core.repositories.topic_type_repository import TopicTypeRepository


def _row_to_type(row: sqlite3.Row) -> TopicType:
    return TopicType(
        k=row["k"],
        label=row["label"],
        short=row["short"],
        color=row["color"],
        ac_hours=row["ac_hours"],
    )


class TopicTypeRepositorySqlLite(TopicTypeRepository):
    """Stores the topic-type catalogue, preserving order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[TopicType]:
        rows = self._conn.execute("SELECT * FROM topic_types ORDER BY rowid").fetchall()
        return [_row_to_type(r) for r in rows]

    def get(self, k: str) -> TopicType | None:
        row = self._conn.execute(
            "SELECT * FROM topic_types WHERE k = ?", (k,)
        ).fetchone()
        return _row_to_type(row) if row else None

    def add(self, topic_type: TopicType) -> None:
        self._conn.execute(
            "INSERT INTO topic_types (k, label, short, color, ac_hours) "
            "VALUES (?, ?, ?, ?, ?)",
            (
                topic_type.k,
                topic_type.label,
                topic_type.short,
                topic_type.color,
                topic_type.ac_hours,
            ),
        )
        self._conn.commit()

    def update(self, topic_type: TopicType) -> None:
        self._conn.execute(
            "UPDATE topic_types SET label = ?, short = ?, color = ?, ac_hours = ? "
            "WHERE k = ?",
            (
                topic_type.label,
                topic_type.short,
                topic_type.color,
                topic_type.ac_hours,
                topic_type.k,
            ),
        )
        self._conn.commit()

    def delete(self, k: str) -> None:
        self._conn.execute("DELETE FROM topic_types WHERE k = ?", (k,))
        self._conn.commit()
