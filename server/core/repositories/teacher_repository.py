"""Abstract port for teacher persistence (teacher + constraints; absences own
their own port).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.teacher import Teacher


class TeacherRepository(ABC):
    """Persistence port for :class:`Teacher` aggregates.

    Implementations hydrate ``constraints`` and ``absences`` when loading.
    """

    @abstractmethod
    def list_all(self) -> list[Teacher]:
        """Return every teacher with constraints and absences populated."""
        raise NotImplementedError

    @abstractmethod
    def get(self, teacher_id: str) -> Teacher | None:
        """Return the teacher with ``teacher_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, teacher: Teacher) -> None:
        """Insert a new teacher (without absences)."""
        raise NotImplementedError

    @abstractmethod
    def update(self, teacher: Teacher) -> None:
        """Persist changes to the teacher row and its constraints."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, teacher_id: str) -> None:
        """Remove the teacher with ``teacher_id`` (no-op if absent)."""
        raise NotImplementedError
