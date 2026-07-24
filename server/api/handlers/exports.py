"""HTTP handlers for export (curriculum/schedule download) resources."""

from __future__ import annotations

from typing import Any

from api.http_types import Body, FileResponse, Params, Query
from api.services.exports import ExportService


class ExportHandlers:
    """Translate export requests to :class:`ExportService` calls."""

    def __init__(self, service: ExportService) -> None:
        self._service = service

    def curriculum(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        return self._service.curriculum(int(body["yearId"]), body.get("period"))

    def schedule(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        return self._service.schedule(
            year_id=int(body["yearId"]),
            period=body["period"],
            view=body.get("view", "group"),
            scope=body.get("scope", "all"),
            entity=body.get("entity"),
        )

    def get(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return self._service.get(params["id"])

    def download(self, params: Params, query: Query, body: Body) -> FileResponse:
        content, filename, content_type = self._service.download(params["id"])
        return FileResponse(content=content, filename=filename, content_type=content_type)
