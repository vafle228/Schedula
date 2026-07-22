"""Abstract port for teacher-absence persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.teacher import Absence


class AbsenceRepository(ABC):
    """Persistence port for :class:`Absence` entities."""

    @abstractmethod
    def list_for_teacher(self, teacher_id: str) -> list[Absence]:
        """Return every absence owned by ``teacher_id``."""
        raise NotImplementedError

    @abstractmethod
    def get(self, absence_id: str) -> Absence | None:
        """Return the absence with ``absence_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, absence: Absence) -> None:
        """Insert a new absence."""
        raise NotImplementedError

    @abstractmethod
    def update(self, absence: Absence) -> None:
        """Persist changes to an existing absence."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, absence_id: str) -> None:
        """Remove the absence with ``absence_id`` (no-op if absent)."""
        raise NotImplementedError
