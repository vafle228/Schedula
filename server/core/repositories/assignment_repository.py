"""Abstract port for topic → teacher assignment persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.assignment import Assignment


class AssignmentRepository(ABC):
    """Persistence port for :class:`Assignment` records (keyed by topic)."""

    @abstractmethod
    def get_all(self) -> dict[str, Assignment]:
        """Return every assignment as a ``topic_id -> Assignment`` map."""
        raise NotImplementedError

    @abstractmethod
    def get(self, topic_id: str) -> Assignment | None:
        """Return the assignment for ``topic_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def set(self, assignment: Assignment) -> None:
        """Insert or replace the assignment for its topic (upsert)."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, topic_id: str) -> None:
        """Remove the assignment for ``topic_id`` (no-op if absent)."""
        raise NotImplementedError
