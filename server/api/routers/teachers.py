"""Route table for teacher resources."""

from __future__ import annotations

from api.handlers.teachers import TeacherHandlers
from api.routers.dispatcher import Router


def register_teacher_routes(router: Router, handlers: TeacherHandlers) -> None:
    router.on("GET", "/teachers", handlers.list)
    router.on("POST", "/teachers", handlers.create)
    router.on("PATCH", "/teachers/:id", handlers.patch)
    router.on("DELETE", "/teachers/:id", handlers.delete)
    router.on("PUT", "/teachers/:id/photo", handlers.put_photo)
    router.on("DELETE", "/teachers/:id/photo", handlers.delete_photo)
    router.on("PUT", "/teachers/:id/constraints", handlers.put_constraints)
