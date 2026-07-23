"""HTTP handlers for teacher resources (profile, photo, constraints)."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.teachers import TeacherService


class TeacherHandlers:
    """Translate teacher requests to :class:`TeacherService` calls."""

    def __init__(self, service: TeacherService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.teacher(teacher) for teacher in self._service.list_all()]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        teacher = self._service.create(name=body.get("name"), photo=body.get("photo"))
        return ser.teacher(teacher)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if body.get("name") is not None:
            changes["name"] = body["name"]
        return ser.teacher(self._service.patch(params["id"], changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(params["id"])
        return None

    def put_photo(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        return ser.teacher(self._service.set_photo(params["id"], body.get("dataUrl")))

    def delete_photo(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.teacher(self._service.set_photo(params["id"], None))

    def put_constraints(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        teacher = self._service.set_constraints(
            params["id"],
            hard=body.get("hard", []),
            soft=body.get("soft", []),
            method=body.get("method"),
            max_per_day=body.get("max"),
        )
        return ser.teacher(teacher)
