"""Abstract port for lesson-slot persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.lesson import Lesson


class LessonRepository(ABC):
    """Persistence port for :class:`Lesson` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Lesson]:
        """Return every lesson (all years) — for global usage guards."""
        raise NotImplementedError

    @abstractmethod
    def list_by_year(self, year_id: int) -> list[Lesson]:
        """Return the year's lessons in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def list_by_year_period(self, year_id: int, period: str) -> list[Lesson]:
        """Return the year's lessons of the given season key."""
        raise NotImplementedError

    @abstractmethod
    def list_by_topic(self, topic_id: int) -> list[Lesson]:
        """Return lessons materialised from ``topic_id`` (across every group)."""
        raise NotImplementedError

    @abstractmethod
    def list_by_group_topic(self, group_id: int, topic_id: int) -> list[Lesson]:
        """Return lessons materialised from ``topic_id`` for one group."""
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

    @abstractmethod
    def delete_by_year(self, year_id: int) -> None:
        """Remove every lesson of ``year_id``."""
        raise NotImplementedError
