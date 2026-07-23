"""Abstract port for group persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.group import Group


class GroupRepository(ABC):
    """Persistence port for :class:`Group` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Group]:
        """Return every group in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def list_by_major(self, major_id: int) -> list[Group]:
        """Return groups owned by ``major_id``."""
        raise NotImplementedError

    @abstractmethod
    def get(self, group_id: str) -> Group | None:
        """Return the group with ``group_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, group: Group) -> None:
        """Insert a new group (``group.id`` is the user-supplied name)."""
        raise NotImplementedError

    @abstractmethod
    def update(self, group: Group) -> None:
        """Persist changes to an existing group."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, group_id: str) -> None:
        """Remove the group with ``group_id`` (no-op if absent)."""
        raise NotImplementedError
