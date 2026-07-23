"""Abstract ports for discipline and topic persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.discipline import Discipline, Topic


class DisciplineRepository(ABC):
    """Persistence port for :class:`Discipline` aggregates.

    Implementations hydrate each discipline's ``topics`` when loading.
    """

    @abstractmethod
    def list_all(self) -> list[Discipline]:
        """Return every discipline with topics populated."""
        raise NotImplementedError

    @abstractmethod
    def get(self, discipline_id: int) -> Discipline | None:
        """Return the discipline with ``discipline_id`` (topics included)."""
        raise NotImplementedError

    @abstractmethod
    def add(self, discipline: Discipline) -> int:
        """Insert a discipline, set ``discipline.id`` to the assigned key, and return it."""
        raise NotImplementedError

    @abstractmethod
    def update(self, discipline: Discipline) -> None:
        """Persist changes to the discipline row (not its topics)."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, discipline_id: int) -> None:
        """Remove the discipline and cascade to its topics."""
        raise NotImplementedError


class TopicRepository(ABC):
    """Persistence port for :class:`Topic` entities."""

    @abstractmethod
    def get(self, topic_id: int) -> Topic | None:
        """Return the topic with ``topic_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def list_by_discipline(self, discipline_id: int) -> list[Topic]:
        """Return topics owned by ``discipline_id``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, topic: Topic) -> int:
        """Insert a new topic, set ``topic.id`` to the assigned key, and return it."""
        raise NotImplementedError

    @abstractmethod
    def update(self, topic: Topic) -> None:
        """Persist changes to an existing topic."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, topic_id: int) -> None:
        """Remove the topic with ``topic_id`` (no-op if absent)."""
        raise NotImplementedError
