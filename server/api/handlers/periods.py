"""HTTP handlers for period (schedule frame) resources."""

from __future__ import annotations

from typing import Any, Final

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.periods import PeriodService
from core.models.period import Slot

_PERIOD_FIELDS: Final[dict[str, str]] = {
    "dateFrom": "date_from", "dateTo": "date_to", "startDate": "start_date",
    "activeDays": "active_days", "acadMin": "acad_min", "slotsPerDay": "slots_per_day",
    "weeksCount": "weeks_count", "holidays": "holidays",
}


class PeriodHandlers:
    """Translate period requests to :class:`PeriodService` calls."""

    def __init__(self, service: PeriodService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.period(period) for period in self._service.list_all()]

    def get(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.period(self._service.get(params["id"]))

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {
            attr: body[camel]
            for camel, attr in _PERIOD_FIELDS.items()
            if camel in body
        }
        if "slots" in body:
            changes["slots"] = [
                Slot(start=slot["start"], hours=slot["hours"], brk=slot.get("brk", 0))
                for slot in body["slots"]
            ]
        return ser.period(self._service.patch(params["id"], changes))
