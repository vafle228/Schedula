"""Route table for per-year semester-settings resources."""

from __future__ import annotations

from api.handlers.settings import SettingsHandlers
from api.routers.dispatcher import Router


def register_settings_routes(router: Router, handlers: SettingsHandlers) -> None:
    router.on("GET", "/settings", handlers.list)
    router.on("GET", "/settings/:period", handlers.get)
    router.on("PATCH", "/settings/:period", handlers.patch)
