"""Abstract port for lesson-slot persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.lesson import Lesson


class LessonRepository(ABC):
    """Persistence port for :class:`Lesson` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Lesson]:
        """Return every lesson in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def list_by_period(self, period: str) -> list[Lesson]:
        """Return lessons of the given season key."""
        raise NotImplementedError

    @abstractmethod
    def list_by_topic(self, topic_id: str) -> list[Lesson]:
        """Return lessons materialised from ``topic_id``."""
        raise NotImplementedError

    @abstractmethod
    def get(self, lesson_id: str) -> Lesson | None:
        """Return the lesson with ``lesson_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, lesson: Lesson) -> None:
        """Insert a new lesson."""
        raise NotImplementedError

    @abstractmethod
    def update(self, lesson: Lesson) -> None:
        """Persist changes to an existing lesson."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, lesson_id: str) -> None:
        """Remove the lesson with ``lesson_id`` (no-op if absent)."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_topic(self, topic_id: str) -> None:
        """Remove every lesson materialised from ``topic_id``."""
        raise NotImplementedError
