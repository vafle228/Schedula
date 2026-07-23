"""HTTP handlers for schedule readiness, generation and conflict analysis."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.services.schedule import ScheduleService


class ScheduleHandlers:
    """Translate schedule requests to :class:`ScheduleService` calls."""

    def __init__(self, service: ScheduleService) -> None:
        self._service = service

    def readiness(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return self._service.readiness(query.get("period") or "fall")

    def generate(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        return self._service.start_generation(
            body.get("period") or "fall", body.get("mode")
        )

    def status(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return self._service.generation_status(params["id"])

    def cancel(self, params: Params, query: Query, body: Body) -> None:
        self._service.cancel_generation(params["id"])
        return None

    def accept(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return self._service.accept_generation(params["id"])

    def conflicts(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        result = self._service.conflicts(query.get("period") or "fall")
        return [
            {"lessonSlotIds": [lesson_id], "issues": issues}
            for lesson_id, issues in result["byId"].items()
        ]
