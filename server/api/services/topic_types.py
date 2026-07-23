"""Application service for topic-type (lesson kind) resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.errors import ApiError
from api.services import ids
from api.services.base import ServiceBase
from core.models.topic_type import TopicType
from core.repositories.discipline_repository import DisciplineRepository
from core.repositories.topic_type_repository import TopicTypeRepository


class TopicTypeService(ServiceBase):
    """List, create, patch and delete the catalogue of lesson kinds."""

    def __init__(
        self, topic_types: TopicTypeRepository, disciplines: DisciplineRepository
    ) -> None:
        self._topic_types = topic_types
        self._disciplines = disciplines

    def list_with_usage(self) -> list[tuple[TopicType, int]]:
        """Return every kind paired with how many topics use it."""
        usage = self._kind_usage()
        return [
            (topic_type, usage.get(topic_type.k, 0))
            for topic_type in self._topic_types.list_all()
        ]

    def create(
        self,
        *,
        label: str,
        short: str | None,
        color: str,
        ac_hours: int,
    ) -> TopicType:
        """Create a lesson kind, deriving a unique key from ``label``."""
        key = ids.slugify_topic_type(
            label, [t.k for t in self._topic_types.list_all()]
        )
        topic_type = TopicType(
            k=key, label=label,
            short=short or ((label or "")[:4] + "."),
            color=color, ac_hours=ac_hours,
        )
        self._topic_types.add(topic_type)
        return topic_type

    def patch(self, k: str, changes: Mapping[str, Any]) -> TopicType:
        """Apply ``changes`` to an existing kind."""
        topic_type = self._require(self._topic_types.get(k), "Тип занятия не найден")
        self._apply(topic_type, changes)
        self._topic_types.update(topic_type)
        return topic_type

    def delete(self, k: str) -> None:
        """Delete a kind, refusing while topics still use it.

        Raises:
            ApiError: ``409`` when the kind is referenced by any topic.
        """
        if k in self._kind_usage():
            raise ApiError(409, "Тип используется в темах")
        self._topic_types.delete(k)

    def _kind_usage(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for discipline in self._disciplines.list_all():
            for topic in discipline.topics:
                counts[topic.kind] = counts.get(topic.kind, 0) + 1
        return counts
