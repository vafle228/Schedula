"""HTTP handlers for per-year semester-settings resources."""

from __future__ import annotations

from typing import Any, Final

from api.http_types import Body, Params, Query, query_year_id
from api.schemas import serialize as ser
from api.services.settings import SettingsService
from core.models.settings import Slot

_SETTINGS_FIELDS: Final[dict[str, str]] = {
    "startDate": "start_date", "activeDays": "active_days", "acadMin": "acad_min",
    "slotsPerDay": "slots_per_day", "weeksCount": "weeks_count", "holidays": "holidays",
}


class SettingsHandlers:
    """Translate settings requests to :class:`SettingsService` calls."""

    def __init__(self, service: SettingsService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        year_id = query_year_id(query)
        year = self._service.year(year_id)
        return [ser.settings(s, year) for s in self._service.list_by_year(year_id)]

    def get(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        year_id = query_year_id(query)
        year = self._service.year(year_id)
        return ser.settings(self._service.get(year_id, params["period"]), year)

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        year_id = query_year_id(query)
        changes: dict[str, Any] = {
            attr: body[camel]
            for camel, attr in _SETTINGS_FIELDS.items()
            if camel in body
        }
        if "slots" in body:
            changes["slots"] = [
                Slot(start=slot["start"], hours=slot["hours"], brk=slot.get("brk", 0))
                for slot in body["slots"]
            ]
        year = self._service.year(year_id)
        updated = self._service.patch(year_id, params["period"], changes)
        return ser.settings(updated, year)
