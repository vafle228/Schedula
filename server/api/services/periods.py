"""Application service for period (schedule frame) resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.services.base import ServiceBase
from core.models.period import Period
from core.repositories.period_repository import PeriodRepository


class PeriodService(ServiceBase):
    """Read and patch the fall/spring scheduling periods."""

    def __init__(self, periods: PeriodRepository) -> None:
        self._periods = periods

    def list_all(self) -> list[Period]:
        """Return every period."""
        return self._periods.list_all()

    def get(self, period_id: str) -> Period:
        """Return a single period or raise ``404``."""
        return self._require(self._periods.get(period_id), "Период не найден")

    def patch(self, period_id: str, changes: Mapping[str, Any]) -> Period:
        """Apply ``changes`` to a period.

        When ``slots`` is present the per-day slot count is re-derived so the
        grid and the bell schedule stay consistent.
        """
        period = self.get(period_id)
        self._apply(period, changes)
        if "slots" in changes:
            period.slots_per_day = len(period.slots)
        self._periods.save(period)
        return period
