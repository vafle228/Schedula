"""Application service for topic resources (nested under disciplines)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.services.base import ServiceBase
from api.services.sync import LessonSyncService
from core.models.discipline import Topic
from core.repositories.discipline_repository import (
    DisciplineRepository,
    TopicRepository,
)
from core.repositories.lesson_repository import LessonRepository


class TopicService(ServiceBase):
    """Create, patch and delete the topics of a discipline."""

    def __init__(
        self,
        topics: TopicRepository,
        disciplines: DisciplineRepository,
        lessons: LessonRepository,
        sync: LessonSyncService,
    ) -> None:
        self._topics = topics
        self._disciplines = disciplines
        self._lessons = lessons
        self._sync = sync

    def create(
        self, discipline_id: int, *, kind: str, name: str, hours: int
    ) -> Topic:
        """Create a topic under an existing discipline.

        Raises:
            ApiError: ``404`` when the discipline does not exist.
        """
        self._require(
            self._disciplines.get(discipline_id), "Дисциплина не найдена"
        )
        topic = Topic(id=0, discipline_id=discipline_id, kind=kind, name=name, hours=hours)
        self._topics.add(topic)
        return topic

    def patch(self, topic_id: int, changes: Mapping[str, Any]) -> Topic:
        """Apply ``changes`` and re-sync lessons when the topic is assigned."""
        topic = self._require(self._topics.get(topic_id), "Тема не найдена")
        self._apply(topic, changes)
        self._topics.update(topic)
        # Re-sync every group assigned to the topic (no-op when unassigned).
        self._sync.sync_topic(topic.id)
        return self._require(self._topics.get(topic.id), "Тема не найдена")

    def delete(self, topic_id: int) -> None:
        """Delete a topic together with its assignments and lessons.

        Every group's assignment for the topic cascades off the topic's FK; its
        lessons carry no cascade and are cleared explicitly.

        Raises:
            ApiError: ``404`` when the topic does not exist.
        """
        self._require(self._topics.get(topic_id), "Тема не найдена")
        self._lessons.delete_by_topic(topic_id)
        self._topics.delete(topic_id)
