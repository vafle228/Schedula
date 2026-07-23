"""Route table for room (classroom) resources."""

from __future__ import annotations

from api.handlers.rooms import RoomHandlers
from api.routers.dispatcher import Router


def register_room_routes(router: Router, handlers: RoomHandlers) -> None:
    router.on("GET", "/rooms", handlers.list)
    router.on("POST", "/rooms", handlers.create)
    router.on("PATCH", "/rooms/:id", handlers.patch)
    router.on("DELETE", "/rooms/:id", handlers.delete)
