"""Route table for academic-year resources."""

from __future__ import annotations

from api.handlers.years import YearHandlers
from api.routers.dispatcher import Router


def register_year_routes(router: Router, handlers: YearHandlers) -> None:
    router.on("GET", "/years", handlers.list)
    router.on("POST", "/years", handlers.create)
    router.on("POST", "/years/:id/activate", handlers.activate)
    router.on("POST", "/years/:id/rollover", handlers.rollover)
    router.on("DELETE", "/years/:id", handlers.delete)
