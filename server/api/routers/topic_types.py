"""Route table for topic-type resources."""

from __future__ import annotations

from api.handlers.topic_types import TopicTypeHandlers
from api.routers.dispatcher import Router


def register_topic_type_routes(router: Router, handlers: TopicTypeHandlers) -> None:
    router.on("GET", "/topic-types", handlers.list)
    router.on("POST", "/topic-types", handlers.create)
    router.on("PATCH", "/topic-types/:k", handlers.patch)
    router.on("DELETE", "/topic-types/:k", handlers.delete)
