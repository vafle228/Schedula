"""Abstract port for major (специальность) persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.major import Major


class MajorRepository(ABC):
    """Persistence port for :class:`Major` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Major]:
        """Return every major in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def get(self, major_id: int) -> Major | None:
        """Return the major with ``major_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, major: Major) -> int:
        """Insert a new major, set ``major.id`` to the assigned key, and return it."""
        raise NotImplementedError

    @abstractmethod
    def update(self, major: Major) -> None:
        """Persist changes to an existing major."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, major_id: int) -> None:
        """Remove the major with ``major_id`` (no-op if absent)."""
        raise NotImplementedError
