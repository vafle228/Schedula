"""Route table for major (specialty) resources."""

from __future__ import annotations

from api.handlers.majors import MajorHandlers
from api.routers.dispatcher import Router


def register_major_routes(router: Router, handlers: MajorHandlers) -> None:
    router.on("GET", "/majors", handlers.list)
    router.on("POST", "/majors", handlers.create)
    router.on("PATCH", "/majors/:id", handlers.patch)
    router.on("DELETE", "/majors/:id", handlers.delete)
