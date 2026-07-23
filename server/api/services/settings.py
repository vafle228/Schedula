"""Application service for per-year semester settings (schedule frame)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.services.base import ServiceBase
from core.models.academic_year import AcademicYear
from core.models.settings import SemesterSettings
from core.repositories.academic_year_repository import AcademicYearRepository
from core.repositories.settings_repository import SettingsRepository


class SettingsService(ServiceBase):
    """Read and patch a year's fall/spring semester settings."""

    def __init__(
        self, settings: SettingsRepository, years: AcademicYearRepository
    ) -> None:
        self._settings = settings
        self._years = years

    def year(self, year_id: int) -> AcademicYear:
        """Return the owning year (used to derive serialized calendar dates)."""
        return self._require(self._years.get(year_id), "Учебный год не найден")

    def list_by_year(self, year_id: int) -> list[SemesterSettings]:
        """Return the year's two semester settings (autumn first)."""
        return self._settings.list_by_year(year_id)

    def get(self, year_id: int, period: str) -> SemesterSettings:
        """Return one semester's settings or raise ``404``."""
        return self._require(
            self._settings.get(year_id, period), "Настройки семестра не найдены"
        )

    def patch(
        self, year_id: int, period: str, changes: Mapping[str, Any]
    ) -> SemesterSettings:
        """Apply ``changes`` to a year's semester settings.

        When ``slots`` is present the per-day slot count is re-derived so the
        grid and the bell schedule stay consistent.
        """
        settings = self.get(year_id, period)
        self._apply(settings, changes)
        if "slots" in changes:
            settings.slots_per_day = len(settings.slots)
        self._settings.save(settings)
        return settings
