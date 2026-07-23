"""Route table for topic resources."""

from __future__ import annotations

from api.handlers.topics import TopicHandlers
from api.routers.dispatcher import Router


def register_topic_routes(router: Router, handlers: TopicHandlers) -> None:
    router.on("POST", "/disciplines/:id/topics", handlers.create)
    router.on("PATCH", "/topics/:id", handlers.patch)
    router.on("DELETE", "/topics/:id", handlers.delete)
