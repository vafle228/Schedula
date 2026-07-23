"""HTTP handlers for room (classroom) resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.rooms import RoomService


class RoomHandlers:
    """Translate classroom requests to :class:`RoomService` calls."""

    def __init__(self, service: RoomService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [
            ser.room(room, used=used)
            for room, used in self._service.list_with_usage()
        ]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        room = self._service.create(
            room_id=body.get("id"),
            room_type=body.get("type"),
            capacity=body.get("capacity"),
        )
        return ser.room(room)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if "capacity" in body:
            changes["capacity"] = body["capacity"]
        if "type" in body:
            changes["type"] = body["type"]
        return ser.room(self._service.patch(params["id"], changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(params["id"])
        return None
