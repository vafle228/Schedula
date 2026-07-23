"""Route table for period resources."""

from __future__ import annotations

from api.handlers.periods import PeriodHandlers
from api.routers.dispatcher import Router


def register_period_routes(router: Router, handlers: PeriodHandlers) -> None:
    router.on("GET", "/periods", handlers.list)
    router.on("GET", "/periods/:id", handlers.get)
    router.on("PATCH", "/periods/:id", handlers.patch)
