"""HTTP handlers for group resources (including major-nested listing/creation)."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.groups import GroupService


class GroupHandlers:
    """Translate group requests to :class:`GroupService` calls."""

    def __init__(self, service: GroupService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.group(group) for group in self._service.list_all()]

    def list_by_major(
        self, params: Params, query: Query, body: Body
    ) -> list[dict[str, Any]]:
        return [ser.group(group) for group in self._service.list_by_major(params["id"])]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        group = self._service.create(
            params["id"], name=body.get("name"), course=body.get("course")
        )
        return ser.group(group)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if body.get("course") is not None:
            changes["course"] = body["course"]
        if body.get("majorId") is not None:
            changes["major_id"] = body["majorId"]
        return ser.group(self._service.patch(params["id"], changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(params["id"])
        return None
