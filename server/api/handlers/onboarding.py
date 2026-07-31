"""HTTP handlers for the first-run onboarding tour."""

from __future__ import annotations

from typing import Any, Final

from api.errors import ApiError
from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.onboarding import OnboardingService
from core.models.onboarding import DataChoice, OnboardingStatus

_PROGRESS_FIELDS: Final[dict[str, str]] = {
    "status": "status",
    "currentStep": "current_step",
    "completedSteps": "completed_steps",
    "dataChoice": "data_choice",
}


def _coerce(attr: str, value: Any) -> Any:
    """Map a raw JSON value onto the enum the model expects."""
    try:
        if attr == "status":
            return OnboardingStatus(value)
        if attr == "data_choice":
            return DataChoice(value) if value else None
    except ValueError as error:
        raise ApiError(400, "Недопустимое значение поля обучения") from error
    return value


class OnboardingHandlers:
    """Translate onboarding requests to :class:`OnboardingService` calls."""

    def __init__(self, service: OnboardingService) -> None:
        self._service = service

    def get(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.onboarding(
            self._service.get(), can_start_clean=self._service.may_start_clean()
        )

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes: dict[str, Any] = {
            attr: _coerce(attr, body[camel])
            for camel, attr in _PROGRESS_FIELDS.items()
            if camel in body
        }
        return ser.onboarding(
            self._service.patch(changes),
            can_start_clean=self._service.may_start_clean(),
        )

    def restart(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.onboarding(
            self._service.restart(),
            can_start_clean=self._service.may_start_clean(),
        )

    def start_clean(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        year = self._service.start_clean()
        return {
            "year": ser.year(year),
            "onboarding": ser.onboarding(
                self._service.get(), can_start_clean=self._service.may_start_clean()
            ),
        }
