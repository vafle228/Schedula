"""HTTP handlers for academic-year resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.years import YearService


class YearHandlers:
    """Translate academic-year requests to :class:`YearService` calls."""

    def __init__(self, service: YearService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.year(year) for year in self._service.list_all()]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        year = self._service.create(
            name=body.get("name"),
            aut_from=body.get("autFrom"), aut_to=body.get("autTo"),
            spr_from=body.get("sprFrom"), spr_to=body.get("sprTo"),
        )
        return ser.year(year)

    def activate(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.year(year) for year in self._service.activate(params["id"])]

    def delete(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.year(year) for year in self._service.delete(params["id"])]
