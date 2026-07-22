"""Abstract port for academic-year persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.academic_year import AcademicYear


class AcademicYearRepository(ABC):
    """Persistence port for :class:`AcademicYear` aggregates."""

    @abstractmethod
    def list_all(self) -> list[AcademicYear]:
        """Return every academic year in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def get(self, year_id: str) -> AcademicYear | None:
        """Return the year with ``year_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, year: AcademicYear) -> None:
        """Insert a new academic year."""
        raise NotImplementedError

    @abstractmethod
    def update(self, year: AcademicYear) -> None:
        """Persist changes to an existing academic year."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, year_id: str) -> None:
        """Remove the year with ``year_id`` (no-op if absent)."""
        raise NotImplementedError
