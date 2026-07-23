"""Application service for room (classroom) resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.room import Room
from core.repositories.lesson_repository import LessonRepository
from core.repositories.room_repository import RoomRepository


class RoomService(ServiceBase):
    """List, create, patch and delete classrooms."""

    def __init__(self, rooms: RoomRepository, lessons: LessonRepository) -> None:
        self._rooms = rooms
        self._lessons = lessons

    def list_with_usage(self) -> list[tuple[Room, int]]:
        """Return every room paired with the number of lessons using it."""
        lessons = self._lessons.list_all()
        return [
            (room, sum(1 for l in lessons if l.room_id == room.id))
            for room in self._rooms.list_all()
        ]

    def create(self, room_id: str, room_type: str, capacity: int) -> Room:
        """Create a classroom.

        Raises:
            ApiError: ``409`` when a room with the same id already exists.
        """
        if any(r.id.lower() == room_id.lower() for r in self._rooms.list_all()):
            raise ApiError(409, "Аудитория уже есть")
        room = Room(id=room_id, type=room_type, capacity=capacity)
        self._rooms.add(room)
        return room

    def patch(self, room_id: str, changes: Mapping[str, Any]) -> Room:
        """Apply ``changes`` to an existing classroom."""
        room = self._require(self._rooms.get(room_id), "Аудитория не найдена")
        self._apply(room, changes)
        self._rooms.update(room)
        return room

    def delete(self, room_id: str) -> None:
        """Delete a classroom, refusing while lessons are scheduled in it.

        Raises:
            ApiError: ``409`` when lessons still reference the room.
        """
        if any(l.room_id == room_id for l in self._lessons.list_all()):
            raise ApiError(409, "На аудиторию назначены пары")
        self._rooms.delete(room_id)
