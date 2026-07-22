"""SQLite adapter for :class:`RoomRepository`."""

from __future__ import annotations

import sqlite3

from core.models.room import Room
from core.repositories.room_repository import RoomRepository


def _row_to_room(row: sqlite3.Row) -> Room:
    return Room(id=row["id"], type=row["type"], capacity=row["capacity"])


class RoomRepositorySqlLite(RoomRepository):
    """Stores rooms, preserving insertion order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[Room]:
        rows = self._conn.execute("SELECT * FROM rooms ORDER BY rowid").fetchall()
        return [_row_to_room(r) for r in rows]

    def get(self, room_id: str) -> Room | None:
        row = self._conn.execute(
            "SELECT * FROM rooms WHERE id = ?", (room_id,)
        ).fetchone()
        return _row_to_room(row) if row else None

    def add(self, room: Room) -> None:
        self._conn.execute(
            "INSERT INTO rooms (id, type, capacity) VALUES (?, ?, ?)",
            (room.id, room.type, room.capacity),
        )
        self._conn.commit()

    def update(self, room: Room) -> None:
        self._conn.execute(
            "UPDATE rooms SET type = ?, capacity = ? WHERE id = ?",
            (room.type, room.capacity, room.id),
        )
        self._conn.commit()

    def delete(self, room_id: str) -> None:
        self._conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        self._conn.commit()
