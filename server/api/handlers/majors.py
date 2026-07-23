"""HTTP handlers for major (specialty) resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.majors import MajorService


class MajorHandlers:
    """Translate major requests to :class:`MajorService` calls."""

    def __init__(self, service: MajorService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [
            ser.major(major, groups_count=count)
            for major, count in self._service.list_with_counts()
        ]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        major = self._service.create(code=body.get("code"), name=body.get("name"))
        return ser.major(major)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if "code" in body:
            changes["code"] = body["code"]
        if "name" in body:
            changes["name"] = body["name"]
        return ser.major(self._service.patch(params["id"], changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(params["id"])
        return None
