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
    def list_by_topic(self, topic_id: int) -> list[Lesson]:
        """Return lessons materialised from ``topic_id``."""
        raise NotImplementedError

    @abstractmethod
    def get(self, lesson_id: int) -> Lesson | None:
        """Return the lesson with ``lesson_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, lesson: Lesson) -> int:
        """Insert a new lesson, set ``lesson.id`` to the assigned key, and return it."""
        raise NotImplementedError

    @abstractmethod
    def update(self, lesson: Lesson) -> None:
        """Persist changes to an existing lesson."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, lesson_id: int) -> None:
        """Remove the lesson with ``lesson_id`` (no-op if absent)."""
        raise NotImplementedError

    @abstractmethod
    def delete_by_topic(self, topic_id: int) -> None:
        """Remove every lesson materialised from ``topic_id``."""
        raise NotImplementedError
