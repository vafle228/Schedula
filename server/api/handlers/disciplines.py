"""HTTP handlers for discipline resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.disciplines import DisciplineService


class DisciplineHandlers:
    """Translate discipline requests to :class:`DisciplineService` calls."""

    def __init__(self, service: DisciplineService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.discipline(d) for d in self._service.list_all()]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        topic_specs = [
            (spec["kind"], spec["name"], spec["hours"])
            for spec in body.get("topics") or []
        ]
        discipline = self._service.create(
            name=body.get("name"),
            group_id=body.get("groupId"),
            period=body.get("period"),
            topic_specs=topic_specs,
        )
        return ser.discipline(discipline)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if "name" in body:
            changes["name"] = body["name"]
        if "groupId" in body:
            changes["group_id"] = body["groupId"]
        if "period" in body:
            changes["period"] = body["period"]
        if "isNew" in body:
            changes["is_new"] = body["isNew"]
        return ser.discipline(self._service.patch(params["id"], changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(params["id"])
        return None
