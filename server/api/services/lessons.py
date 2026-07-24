"""Application service for lesson (scheduled pair) resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.services.base import ServiceBase
from core.models.lesson import Lesson
from core.repositories.discipline_repository import TopicRepository
from core.repositories.lesson_repository import LessonRepository


class LessonService(ServiceBase):
    """List, create, patch, and delete scheduled lessons."""

    def __init__(self, lessons: LessonRepository, topics: TopicRepository) -> None:
        self._lessons = lessons
        self._topics = topics

    def list_by_year(self, year_id: int) -> list[Lesson]:
        """Return the year's lessons."""
        return self._lessons.list_by_year(year_id)

    def create(self, data: Mapping[str, Any]) -> Lesson:
        """Create a lesson from a snake-cased attribute map.

        The discipline defaults to the source topic's when omitted; the id is
        always assigned by the database.
        """
        topic_id: int | None = data.get("topic_id") or None
        topic = self._topics.get(topic_id) if topic_id else None
        discipline_id: int | None = data.get("discipline_id") or (
            topic.discipline_id if topic else None
        )
        lesson = Lesson(
            id=0,
            year_id=data.get("year_id"),
            topic_id=topic_id, discipline_id=discipline_id,
            group_id=data.get("group_id"), teacher_id=data.get("teacher_id"),
            room_id=data.get("room_id"), kind=data.get("kind"),
            period=data.get("period"),
            week=data.get("week"), day=data.get("day"), slot=data.get("slot"),
            sub_by=data.get("sub_by") or None,
            manual=data.get("manual") is not False,
            ni=data.get("ni") or 1, nt=data.get("nt") or 1,
            topic_label=data.get("topic_label") or "",
            question=data.get("question") or "",
            number=data.get("number") or None,
        )
        self._lessons.add(lesson)
        return lesson

    def patch(self, lesson_id: int, changes: Mapping[str, Any]) -> Lesson:
        """Apply ``changes`` to an existing lesson."""
        lesson = self._get(lesson_id)
        self._apply(lesson, changes)
        self._lessons.update(lesson)
        return lesson

    def delete(self, lesson_id: int) -> None:
        """Delete a lesson (no-op if it is already gone)."""
        self._lessons.delete(lesson_id)

    def _get(self, lesson_id: int) -> Lesson:
        return self._require(self._lessons.get(lesson_id), "Занятие не найдено")
