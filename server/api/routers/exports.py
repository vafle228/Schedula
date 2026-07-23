"""Route table for export resources."""

from __future__ import annotations

from api.handlers.exports import ExportHandlers
from api.routers.dispatcher import Router


def register_export_routes(router: Router, handlers: ExportHandlers) -> None:
    router.on("POST", "/exports/curriculum", handlers.curriculum)
    router.on("POST", "/exports/schedule", handlers.schedule)
    router.on("GET", "/exports/:id", handlers.get)
