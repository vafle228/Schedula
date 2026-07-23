"""Route table for group resources (including major-nested endpoints)."""

from __future__ import annotations

from api.handlers.groups import GroupHandlers
from api.routers.dispatcher import Router


def register_group_routes(router: Router, handlers: GroupHandlers) -> None:
    router.on("GET", "/groups", handlers.list)
    router.on("GET", "/majors/:id/groups", handlers.list_by_major)
    router.on("POST", "/majors/:id/groups", handlers.create)
    router.on("PATCH", "/groups/:id", handlers.patch)
    router.on("DELETE", "/groups/:id", handlers.delete)
