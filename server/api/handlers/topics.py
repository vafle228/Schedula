"""HTTP handlers for topic resources (nested under disciplines)."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.topics import TopicService


class TopicHandlers:
    """Translate topic requests to :class:`TopicService` calls."""

    def __init__(self, service: TopicService) -> None:
        self._service = service

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        topic = self._service.create(
            int(params["id"]),
            kind=body.get("kind"), name=body.get("name"), hours=body.get("hours"),
        )
        return ser.topic(topic)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if "kind" in body:
            changes["kind"] = body["kind"]
        if "name" in body:
            changes["name"] = body["name"]
        if "hours" in body:
            changes["hours"] = body["hours"]
        return ser.topic(self._service.patch(int(params["id"]), changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(int(params["id"]))
        return None
