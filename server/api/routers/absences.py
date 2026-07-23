"""Route table for teacher absence resources."""

from __future__ import annotations

from api.handlers.absences import AbsenceHandlers
from api.routers.dispatcher import Router


def register_absence_routes(router: Router, handlers: AbsenceHandlers) -> None:
    router.on("POST", "/teachers/:id/absences", handlers.create)
    router.on("PATCH", "/absences/:id", handlers.patch)
    router.on("DELETE", "/absences/:id", handlers.delete)
