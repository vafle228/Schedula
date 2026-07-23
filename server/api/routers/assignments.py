"""Route table for topic/teacher assignment resources."""

from __future__ import annotations

from api.handlers.assignments import AssignmentHandlers
from api.routers.dispatcher import Router


def register_assignment_routes(router: Router, handlers: AssignmentHandlers) -> None:
    router.on("GET", "/assignments", handlers.list)
    router.on("PUT", "/topics/:id/assignment", handlers.put)
    router.on("DELETE", "/topics/:id/assignment", handlers.delete)
    router.on("POST", "/disciplines/:id/assignment", handlers.assign_discipline)
    router.on("POST", "/assignments/batch", handlers.batch)
