"""Route table for the first-run onboarding tour."""

from __future__ import annotations

from api.handlers.onboarding import OnboardingHandlers
from api.routers.dispatcher import Router


def register_onboarding_routes(router: Router, handlers: OnboardingHandlers) -> None:
    router.on("GET", "/onboarding", handlers.get)
    router.on("PATCH", "/onboarding", handlers.patch)
    router.on("POST", "/onboarding/restart", handlers.restart)
    router.on("POST", "/onboarding/start-clean", handlers.start_clean)
