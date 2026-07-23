"""HTTP handlers for topic/teacher assignment resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.assignments import AssignmentService


class AssignmentHandlers:
    """Translate assignment requests to :class:`AssignmentService` calls."""

    def __init__(self, service: AssignmentService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.assignments_map(self._service.list_all())

    def put(self, params: Params, query: Query, body: Body) -> dict[str, Any] | None:
        assert body is not None
        current = self._service.set(params["id"], body.get("teacherId"))
        return ser.assignment(current) if current else None

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.clear(params["id"])
        return None

    def assign_discipline(
        self, params: Params, query: Query, body: Body
    ) -> dict[str, list[str]]:
        assert body is not None
        touched = self._service.assign_discipline(params["id"], body.get("teacherId"))
        return {"topicIds": touched}

    def batch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        ops = [
            (op["topicId"], op.get("teacherId")) for op in body.get("ops") or []
        ]
        return ser.assignments_map(self._service.batch(ops))
