"""HTTP handlers for academic-year resources (including roll-over)."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.rollover import RolloverService
from api.services.years import YearService


class YearHandlers:
    """Translate academic-year requests to service calls."""

    def __init__(self, service: YearService, rollover: RolloverService) -> None:
        self._service = service
        self._rollover = rollover

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.year(year) for year in self._service.list_all()]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        copy_from = body.get("copyFromYearId")
        year = self._service.create(
            name=body.get("name"),
            aut_from=body.get("autFrom"), aut_to=body.get("autTo"),
            spr_from=body.get("sprFrom"), spr_to=body.get("sprTo"),
            copy_from_year_id=int(copy_from) if copy_from is not None else None,
        )
        return ser.year(year)

    def activate(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.year(year) for year in self._service.activate(int(params["id"]))]

    def delete(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.year(year) for year in self._service.delete(int(params["id"]))]

    def rollover(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        assert body is not None
        ids = body.get("disciplineIds")
        created = self._rollover.rollover(
            target_year_id=int(params["id"]),
            source_year_id=int(body["sourceYearId"]),
            discipline_ids=[int(i) for i in ids] if ids is not None else None,
        )
        return [ser.discipline(d) for d in created]
