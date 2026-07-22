"""Abstract port for topic-type catalogue persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.topic_type import TopicType


class TopicTypeRepository(ABC):
    """Persistence port for :class:`TopicType` catalogue entries."""

    @abstractmethod
    def list_all(self) -> list[TopicType]:
        """Return every topic type in catalogue order."""
        raise NotImplementedError

    @abstractmethod
    def get(self, k: str) -> TopicType | None:
        """Return the type with key ``k`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, topic_type: TopicType) -> None:
        """Insert a new topic type."""
        raise NotImplementedError

    @abstractmethod
    def update(self, topic_type: TopicType) -> None:
        """Persist changes to an existing topic type."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, k: str) -> None:
        """Remove the type with key ``k`` (no-op if absent)."""
        raise NotImplementedError
