"""Route table for lesson (scheduled pair) resources."""

from __future__ import annotations

from api.handlers.lessons import LessonHandlers
from api.routers.dispatcher import Router


def register_lesson_routes(router: Router, handlers: LessonHandlers) -> None:
    router.on("GET", "/lessons", handlers.list)
    router.on("POST", "/lessons", handlers.create)
    router.on("PATCH", "/lessons/:id", handlers.patch)
    router.on("DELETE", "/lessons/:id", handlers.delete)
    router.on("PUT", "/lessons/:id/pin", handlers.pin)
    router.on("DELETE", "/lessons/:id/pin", handlers.unpin)
