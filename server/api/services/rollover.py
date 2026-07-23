"""Roll-over service — copy a curated set of disciplines into a draft year.

The academic plan recurs year to year (Математика every year, a course-specific
"C# web development" only while its major runs), but which disciplines carry
over is a human decision, not a rule worth encoding. So the client presents the
source year's disciplines as a checklist — all ticked — and the user unticks the
ones the new year should not inherit; the chosen ids arrive here.

Only the plan travels: each selected discipline is cloned with its topics and
re-pointed at the same (global) major. Groups, teachers and assignments are
recreated from scratch in the new year, so nothing here depends on them.
"""

from __future__ import annotations

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.academic_year import YearStatus
from core.models.discipline import Discipline, Topic
from core.repositories.academic_year_repository import AcademicYearRepository
from core.repositories.discipline_repository import DisciplineRepository


class RolloverService(ServiceBase):
    """Clone selected disciplines from one academic year into a draft year."""

    def __init__(
        self,
        *,
        years: AcademicYearRepository,
        disciplines: DisciplineRepository,
    ) -> None:
        self._years = years
        self._disciplines = disciplines

    def source_disciplines(self, source_year_id: int) -> list[Discipline]:
        """Return a source year's disciplines to populate the copy checklist.

        Raises:
            ApiError: ``404`` when the source year is missing.
        """
        self._require(
            self._years.get(source_year_id), "Исходный учебный год не найден"
        )
        return self._disciplines.list_by_year(source_year_id)

    def rollover(
        self,
        target_year_id: int,
        source_year_id: int,
        discipline_ids: list[int] | None,
    ) -> list[Discipline]:
        """Copy the chosen disciplines from ``source`` into the draft ``target``.

        Args:
            target_year_id: The draft year to populate.
            source_year_id: The year whose plan is copied.
            discipline_ids: The disciplines to carry over; ``None`` copies all.

        Returns:
            The freshly created disciplines.

        Raises:
            ApiError: ``404`` when either year is missing; ``409`` when the
                target is not a draft or already holds disciplines.
        """
        target = self._require(
            self._years.get(target_year_id), "Целевой учебный год не найден"
        )
        self._require(
            self._years.get(source_year_id), "Исходный учебный год не найден"
        )
        if target.status != YearStatus.DRAFT:
            raise ApiError(409, "Переносить можно только в черновой год")
        if self._disciplines.list_by_year(target_year_id):
            raise ApiError(409, "В целевом году уже есть дисциплины")

        wanted = set(discipline_ids) if discipline_ids is not None else None
        copied: list[Discipline] = []
        for src in self._disciplines.list_by_year(source_year_id):
            if wanted is not None and src.id not in wanted:
                continue
            copied.append(self._clone_discipline(src, target_year_id))
        return copied

    def _clone_discipline(self, src: Discipline, target_year_id: int) -> Discipline:
        """Copy one discipline (with its topics) into the target year."""
        clone = Discipline(
            id=0,
            year_id=target_year_id,
            name=src.name,
            major_id=src.major_id,
            course=src.course,
            period=src.period,
            is_new=False,
            topics=[
                Topic(id=0, discipline_id=0, kind=t.kind, name=t.name, hours=t.hours)
                for t in src.topics
            ],
        )
        self._disciplines.add(clone)
        return clone
