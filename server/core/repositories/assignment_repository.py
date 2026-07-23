"""Abstract port for topic → teacher assignment persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.assignment import Assignment


Key = tuple[int, int]
"""An assignment key — the ``(group_id, topic_id)`` pair."""


class AssignmentRepository(ABC):
    """Persistence port for :class:`Assignment` records (keyed by group+topic)."""

    @abstractmethod
    def get_all(self) -> dict[Key, Assignment]:
        """Return every assignment as a ``(group_id, topic_id) -> Assignment`` map."""
        raise NotImplementedError

    @abstractmethod
    def list_by_year(self, year_id: int) -> dict[Key, Assignment]:
        """Return the year's assignments keyed by ``(group_id, topic_id)``.

        Scoped via the owning topic's discipline year.
        """
        raise NotImplementedError

    @abstractmethod
    def list_by_topic(self, topic_id: int) -> list[Assignment]:
        """Return every group's assignment for ``topic_id``."""
        raise NotImplementedError

    @abstractmethod
    def get(self, group_id: int, topic_id: int) -> Assignment | None:
        """Return the assignment for ``(group_id, topic_id)`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def set(self, assignment: Assignment) -> None:
        """Insert or replace the assignment for its ``(group, topic)`` (upsert)."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, group_id: int, topic_id: int) -> None:
        """Remove the assignment for ``(group_id, topic_id)`` (no-op if absent)."""
        raise NotImplementedError
