"""HTTP handlers for topic/teacher assignment resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query, body_year_id, query_year_id
from api.schemas import serialize as ser
from api.services.assignments import AssignmentService


class AssignmentHandlers:
    """Translate assignment requests to :class:`AssignmentService` calls."""

    def __init__(self, service: AssignmentService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.assignments_map(self._service.list_by_year(query_year_id(query)))

    def put(self, params: Params, query: Query, body: Body) -> dict[str, Any] | None:
        assert body is not None
        teacher_id = body.get("teacherId")
        current = self._service.set(
            int(body["groupId"]),
            int(params["id"]),
            int(teacher_id) if teacher_id is not None else None,
        )
        return ser.assignment(current) if current else None

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.clear(int(query["groupId"]), int(params["id"]))
        return None

    def assign_discipline(
        self, params: Params, query: Query, body: Body
    ) -> dict[str, list[int]]:
        assert body is not None
        teacher_id = body.get("teacherId")
        touched = self._service.assign_discipline(
            int(body["groupId"]),
            int(params["id"]),
            int(teacher_id) if teacher_id is not None else None,
        )
        return {"topicIds": touched}

    def batch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        ops = [
            (
                int(op["groupId"]),
                int(op["topicId"]),
                int(op["teacherId"]) if op.get("teacherId") is not None else None,
            )
            for op in body.get("ops") or []
        ]
        return ser.assignments_map(self._service.batch(body_year_id(body), ops))
