"""Route table for discipline resources."""

from __future__ import annotations

from api.handlers.disciplines import DisciplineHandlers
from api.routers.dispatcher import Router


def register_discipline_routes(router: Router, handlers: DisciplineHandlers) -> None:
    router.on("GET", "/disciplines", handlers.list)
    router.on("POST", "/disciplines", handlers.create)
    router.on("PATCH", "/disciplines/:id", handlers.patch)
    router.on("DELETE", "/disciplines/:id", handlers.delete)
