"""Abstract port for group persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.group import Group


class GroupRepository(ABC):
    """Persistence port for :class:`Group` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Group]:
        """Return every group (all years) — for global usage counts."""
        raise NotImplementedError

    @abstractmethod
    def list_by_year(self, year_id: int) -> list[Group]:
        """Return the year's groups in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def list_by_year_major(self, year_id: int, major_id: int) -> list[Group]:
        """Return the year's groups owned by ``major_id``."""
        raise NotImplementedError

    @abstractmethod
    def get(self, group_id: int) -> Group | None:
        """Return the group with ``group_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, group: Group) -> int:
        """Insert a new group, assign and return its integer id."""
        raise NotImplementedError

    @abstractmethod
    def update(self, group: Group) -> None:
        """Persist changes to an existing group."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, group_id: int) -> None:
        """Remove the group with ``group_id`` (no-op if absent)."""
        raise NotImplementedError
