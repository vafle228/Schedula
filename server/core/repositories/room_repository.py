"""Abstract port for room persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.room import Room


class RoomRepository(ABC):
    """Persistence port for :class:`Room` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Room]:
        """Return every room in insertion order."""
        raise NotImplementedError

    @abstractmethod
    def get(self, room_id: str) -> Room | None:
        """Return the room with ``room_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def add(self, room: Room) -> None:
        """Insert a new room."""
        raise NotImplementedError

    @abstractmethod
    def update(self, room: Room) -> None:
        """Persist changes to an existing room."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, room_id: str) -> None:
        """Remove the room with ``room_id`` (no-op if absent)."""
        raise NotImplementedError
