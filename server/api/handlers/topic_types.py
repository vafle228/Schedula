"""HTTP handlers for topic-type (lesson kind) resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.topic_types import TopicTypeService


class TopicTypeHandlers:
    """Translate topic-type requests to :class:`TopicTypeService` calls."""

    def __init__(self, service: TopicTypeService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [
            ser.topic_type(topic_type, used=used)
            for topic_type, used in self._service.list_with_usage()
        ]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        topic_type = self._service.create(
            label=body.get("label"),
            short=body.get("short"),
            color=body.get("color"),
            ac_hours=body.get("acHours") or 2,
        )
        return ser.topic_type(topic_type)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if "label" in body:
            changes["label"] = body["label"]
        if "short" in body:
            changes["short"] = body["short"]
        if "color" in body:
            changes["color"] = body["color"]
        if "acHours" in body:
            changes["ac_hours"] = body["acHours"]
        return ser.topic_type(self._service.patch(params["k"], changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(params["k"])
        return None
