"""Route table for schedule readiness, generation and conflicts."""

from __future__ import annotations

from api.handlers.schedule import ScheduleHandlers
from api.routers.dispatcher import Router


def register_schedule_routes(router: Router, handlers: ScheduleHandlers) -> None:
    router.on("GET", "/schedule/readiness", handlers.readiness)
    router.on("POST", "/schedule/generate", handlers.generate)
    router.on("GET", "/schedule/generate/:id", handlers.status)
    router.on("POST", "/schedule/generate/:id/cancel", handlers.cancel)
    router.on("POST", "/schedule/generate/:id/rollback", handlers.cancel)
    router.on("POST", "/schedule/generate/:id/accept", handlers.accept)
    router.on("GET", "/schedule/conflicts", handlers.conflicts)
