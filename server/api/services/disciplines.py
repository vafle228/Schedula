"""Application service for discipline resources."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from api.services.base import ServiceBase
from core.models.discipline import Discipline, Topic
from core.repositories.discipline_repository import (
    DisciplineRepository,
    TopicRepository,
)
from core.repositories.lesson_repository import LessonRepository


class DisciplineService(ServiceBase):
    """List, create, patch and delete disciplines and their initial topics."""

    def __init__(
        self,
        disciplines: DisciplineRepository,
        topics: TopicRepository,
        lessons: LessonRepository,
    ) -> None:
        self._disciplines = disciplines
        self._topics = topics
        self._lessons = lessons

    def list_by_year(self, year_id: int) -> list[Discipline]:
        """Return the year's disciplines."""
        return self._disciplines.list_by_year(year_id)

    def create(
        self,
        *,
        year_id: int,
        name: str,
        major_id: int,
        course: int,
        period: str,
        topic_specs: Sequence[tuple[str, str, int]],
    ) -> Discipline:
        """Create a discipline and its seed topics (``(kind, name, hours)``)."""
        discipline = Discipline(
            id=0, year_id=year_id, name=name, major_id=major_id, course=course,
            period=period, is_new=True, topics=[],
        )
        self._disciplines.add(discipline)
        for kind, topic_name, hours in topic_specs:
            self._topics.add(Topic(
                id=0,
                discipline_id=discipline.id,
                kind=kind, name=topic_name, hours=hours,
            ))
        return self._require(self._disciplines.get(discipline.id), "Дисциплина не найдена")

    def patch(self, discipline_id: int, changes: Mapping[str, Any]) -> Discipline:
        """Apply ``changes`` to an existing discipline."""
        discipline = self._require(
            self._disciplines.get(discipline_id), "Дисциплина не найдена"
        )
        self._apply(discipline, changes)
        self._disciplines.update(discipline)
        return self._require(
            self._disciplines.get(discipline.id), "Дисциплина не найдена"
        )

    def delete(self, discipline_id: int) -> None:
        """Delete a discipline and the lessons of its topics.

        Topics and assignments cascade in the database; lessons carry no FK
        cascade and are cleared explicitly.
        """
        discipline = self._require(
            self._disciplines.get(discipline_id), "Дисциплина не найдена"
        )
        for topic in discipline.topics:
            self._lessons.delete_by_topic(topic.id)
        self._disciplines.delete(discipline.id)
