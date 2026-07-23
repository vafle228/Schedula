"""Application service for academic-year resources."""

from __future__ import annotations

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.academic_year import AcademicYear, YearStatus
from core.repositories.academic_year_repository import AcademicYearRepository


class YearService(ServiceBase):
    """List, create, activate and delete academic years."""

    def __init__(self, years: AcademicYearRepository) -> None:
        self._years = years

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
    ) -> AcademicYear:
        """Create a draft academic year."""
        year = AcademicYear(
            id=0, name=name,
            aut_from=aut_from, aut_to=aut_to, spr_from=spr_from, spr_to=spr_to,
            status=YearStatus.DRAFT,
        )
        self._years.add(year)
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
        """Delete a draft year and return the remaining list.

        Raises:
            ApiError: ``404`` when missing, ``409`` when the year is active.
        """
        target = self._require(self._years.get(year_id), "Учебный год не найден")
        if target.status == YearStatus.ACTIVE:
            raise ApiError(409, "Активный год удалить нельзя")
        self._years.delete(target.id)
        return self._years.list_all()
