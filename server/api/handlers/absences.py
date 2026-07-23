"""HTTP handlers for teacher absence resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.absences import AbsenceService
from core.models.teacher import AbsenceType


class AbsenceHandlers:
    """Translate absence requests to :class:`AbsenceService` calls."""

    def __init__(self, service: AbsenceService) -> None:
        self._service = service

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        absence = self._service.create(
            int(params["id"]),
            absence_type=AbsenceType(body.get("type")),
            label=body.get("label") or "",
        )
        return ser.absence(absence)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {}
        if "type" in body:
            changes["type"] = AbsenceType(body["type"])
        if "label" in body:
            changes["label"] = body["label"]
        return ser.absence(self._service.patch(int(params["id"]), changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(int(params["id"]))
        return None
