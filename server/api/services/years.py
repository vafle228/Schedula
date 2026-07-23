"""Application service for academic-year resources."""

from __future__ import annotations

from dataclasses import replace

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.academic_year import AcademicYear, YearStatus
from core.models.settings import SemesterSettings, default_settings, ru_to_iso
from core.repositories.academic_year_repository import AcademicYearRepository
from core.repositories.lesson_repository import LessonRepository
from core.repositories.settings_repository import SettingsRepository

_SEASONS: tuple[str, str] = ("fall", "spring")


class YearService(ServiceBase):
    """List, create, activate and delete academic years and their settings."""

    def __init__(
        self,
        years: AcademicYearRepository,
        settings: SettingsRepository,
        lessons: LessonRepository,
    ) -> None:
        self._years = years
        self._settings = settings
        self._lessons = lessons

    def list_all(self) -> list[AcademicYear]:
        """Return every academic year."""
        return self._years.list_all()

    def create(
        self,
        *,
        name: str,
        aut_from: str,
        aut_to: str,
        spr_from: str,
        spr_to: str,
        copy_from_year_id: int | None = None,
    ) -> AcademicYear:
        """Create a draft academic year and its two semester-settings rows.

        When ``copy_from_year_id`` is given, the new settings inherit that year's
        grid (slots / active days / weeks / holidays / academic minute); dates
        always come from the new year. Otherwise the factory defaults are used.
        """
        year = AcademicYear(
            id=0, name=name,
            aut_from=aut_from, aut_to=aut_to, spr_from=spr_from, spr_to=spr_to,
            status=YearStatus.DRAFT,
        )
        self._years.add(year)

        source = (
            {s.period: s for s in self._settings.list_by_year(copy_from_year_id)}
            if copy_from_year_id is not None
            else {}
        )
        starts = {"fall": aut_from, "spring": spr_from}
        for period in _SEASONS:
            template = source.get(period)
            if template is None:
                self._settings.save(default_settings(year.id, period, starts[period]))
            else:
                self._settings.save(replace(
                    template,
                    year_id=year.id,
                    start_date=ru_to_iso(starts[period]),
                    slots=[replace(s) for s in template.slots],
                    active_days=list(template.active_days),
                    holidays=list(template.holidays),
                ))
        return year

    def activate(self, year_id: int) -> list[AcademicYear]:
        """Make ``year_id`` the sole active year and return the full list.

        Raises:
            ApiError: ``404`` when the year does not exist.
        """
        target = self._require(self._years.get(year_id), "Учебный год не найден")
        for year in self._years.list_all():
            if year.id == target.id:
                if year.status != YearStatus.ACTIVE:
                    year.status = YearStatus.ACTIVE
                    self._years.update(year)
            elif year.status == YearStatus.ACTIVE:
                year.status = YearStatus.DRAFT
                self._years.update(year)
        return self._years.list_all()

    def delete(self, year_id: int) -> list[AcademicYear]:
        """Delete a draft year with all its scoped data; return the remaining list.

        Settings, groups, disciplines, topics and assignments cascade via foreign
        keys; lessons carry no cascade and are cleared explicitly.

        Raises:
            ApiError: ``404`` when missing, ``409`` when the year is active.
        """
        target = self._require(self._years.get(year_id), "Учебный год не найден")
        if target.status == YearStatus.ACTIVE:
            raise ApiError(409, "Активный год удалить нельзя")
        self._lessons.delete_by_year(target.id)
        self._years.delete(target.id)
        return self._years.list_all()

    def get_settings(self, year_id: int, period: str) -> SemesterSettings:
        """Return one semester's settings (used to derive serialized dates)."""
        return self._require(
            self._settings.get(year_id, period), "Настройки семестра не найдены"
        )
