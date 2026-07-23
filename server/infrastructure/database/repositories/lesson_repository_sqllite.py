"""SQLite adapter for :class:`LessonRepository`."""

from __future__ import annotations

import sqlite3

from core.models.lesson import Lesson
from core.repositories.lesson_repository import LessonRepository

_COLUMNS = (
    "id, year_id, topic_id, discipline_id, group_id, teacher_id, room_id, kind, "
    "period, week, day, slot, sub_by, pin, manual, ni, nt, topic_label, question"
)


def _row_to_lesson(row: sqlite3.Row) -> Lesson:
    return Lesson(
        id=row["id"],
        year_id=row["year_id"],
        topic_id=row["topic_id"],
        discipline_id=row["discipline_id"],
        group_id=row["group_id"],
        teacher_id=row["teacher_id"],
        room_id=row["room_id"],
        kind=row["kind"],
        period=row["period"],
        week=row["week"],
        day=row["day"],
        slot=row["slot"],
        sub_by=row["sub_by"],
        pin=bool(row["pin"]),
        manual=bool(row["manual"]),
        ni=row["ni"],
        nt=row["nt"],
        topic_label=row["topic_label"],
        question=row["question"],
    )


def _params(lesson: Lesson) -> dict[str, object]:
    return {
        "year_id": lesson.year_id,
        "topic_id": lesson.topic_id,
        "discipline_id": lesson.discipline_id,
        "group_id": lesson.group_id,
        "teacher_id": lesson.teacher_id,
        "room_id": lesson.room_id,
        "kind": lesson.kind,
        "period": lesson.period,
        "week": lesson.week,
        "day": lesson.day,
        "slot": lesson.slot,
        "sub_by": lesson.sub_by,
        "pin": int(lesson.pin),
        "manual": int(lesson.manual),
        "ni": lesson.ni,
        "nt": lesson.nt,
        "topic_label": lesson.topic_label,
        "question": lesson.question,
    }


class LessonRepositorySqlLite(LessonRepository):
    """Stores lesson slots, preserving insertion order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[Lesson]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM lessons ORDER BY rowid"
        ).fetchall()
        return [_row_to_lesson(r) for r in rows]

    def list_by_year(self, year_id: int) -> list[Lesson]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM lessons WHERE year_id = ? ORDER BY rowid",
            (year_id,),
        ).fetchall()
        return [_row_to_lesson(r) for r in rows]

    def list_by_year_period(self, year_id: int, period: str) -> list[Lesson]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM lessons WHERE year_id = ? AND period = ? "
            "ORDER BY rowid",
            (year_id, period),
        ).fetchall()
        return [_row_to_lesson(r) for r in rows]

    def list_by_topic(self, topic_id: int) -> list[Lesson]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM lessons WHERE topic_id = ? ORDER BY rowid",
            (topic_id,),
        ).fetchall()
        return [_row_to_lesson(r) for r in rows]

    def list_by_group_topic(self, group_id: int, topic_id: int) -> list[Lesson]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM lessons WHERE group_id = ? AND topic_id = ? "
            "ORDER BY rowid",
            (group_id, topic_id),
        ).fetchall()
        return [_row_to_lesson(r) for r in rows]

    def get(self, lesson_id: int) -> Lesson | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM lessons WHERE id = ?", (lesson_id,)
        ).fetchone()
        return _row_to_lesson(row) if row else None

    def add(self, lesson: Lesson) -> int:
        p = _params(lesson)
        cursor = self._conn.execute(
            """
            INSERT INTO lessons (year_id, topic_id, discipline_id, group_id, teacher_id,
                    room_id, kind, period, week, day, slot, sub_by,
                    pin, manual, ni, nt, topic_label, question)
            VALUES (:year_id, :topic_id, :discipline_id, :group_id, :teacher_id,
                    :room_id, :kind, :period, :week, :day, :slot, :sub_by,
                    :pin, :manual, :ni, :nt, :topic_label, :question)
            """,
            p,
        )
        self._conn.commit()
        lesson.id = cursor.lastrowid
        return lesson.id

    def update(self, lesson: Lesson) -> None:
        self._conn.execute(
            """
            UPDATE lessons SET
                topic_id = :topic_id, discipline_id = :discipline_id,
                group_id = :group_id, teacher_id = :teacher_id, room_id = :room_id,
                kind = :kind, period = :period, week = :week, day = :day,
                slot = :slot, sub_by = :sub_by, pin = :pin, manual = :manual,
                ni = :ni, nt = :nt, topic_label = :topic_label, question = :question
            WHERE id = :id
            """,
            {**_params(lesson), "id": lesson.id},
        )
        self._conn.commit()

    def delete(self, lesson_id: int) -> None:
        self._conn.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
        self._conn.commit()

    def delete_by_topic(self, topic_id: int) -> None:
        self._conn.execute("DELETE FROM lessons WHERE topic_id = ?", (topic_id,))
        self._conn.commit()

    def delete_by_year(self, year_id: int) -> None:
        self._conn.execute("DELETE FROM lessons WHERE year_id = ?", (year_id,))
        self._conn.commit()
