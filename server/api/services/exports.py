"""Application service for export (curriculum/schedule download) resources.

A curriculum export renders the state teaching-load template into a real
``.xlsx`` (see :mod:`api.services.curriculum_export`); the bytes are held in
memory keyed by the issued export id and streamed back by the download endpoint.
Schedule exports remain descriptor-only stubs for now.
"""

from __future__ import annotations

from dataclasses import dataclass

from api.errors import ApiError
from api.services.base import ServiceBase
from api.services.curriculum_export import build_curriculum_workbook
from core.repositories.academic_year_repository import AcademicYearRepository
from core.repositories.assignment_repository import AssignmentRepository
from core.repositories.discipline_repository import DisciplineRepository
from core.repositories.group_repository import GroupRepository
from core.repositories.major_repository import MajorRepository
from core.repositories.teacher_repository import TeacherRepository

_XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@dataclass(slots=True)
class _Export:
    """An issued export: its download filename and the generated file bytes."""

    id: str
    file_name: str
    content: bytes | None
    content_type: str


class ExportService(ServiceBase):
    """Issues export descriptors and holds the generated curriculum files."""

    def __init__(
        self,
        teachers: TeacherRepository,
        disciplines: DisciplineRepository,
        groups: GroupRepository,
        assignments: AssignmentRepository,
        majors: MajorRepository,
        years: AcademicYearRepository,
    ) -> None:
        self._teachers = teachers
        self._disciplines = disciplines
        self._groups = groups
        self._assignments = assignments
        self._majors = majors
        self._years = years
        self._exports: dict[str, _Export] = {}
        self._counter = 0

    def curriculum(self, year_id: int, period: str) -> dict[str, str]:
        """Generate the teaching-load workbook for ``year_id`` / ``period``."""
        year = self._require(self._years.get(year_id), "Учебный год не найден")
        label = _year_label(year.aut_from)
        content = build_curriculum_workbook(
            year_label=label,
            period=period,
            teachers=self._teachers.list_all(),
            disciplines=self._disciplines.list_by_year(year_id),
            groups=self._groups.list_by_year(year_id),
            assignments=self._assignments.list_by_year(year_id),
            majors=self._majors.list_all(),
        )
        export_id = self._new_id()
        self._exports[export_id] = _Export(
            id=export_id,
            file_name=f"Учебный_план_{label}{_period_suffix(period)}.xlsx",
            content=content,
            content_type=_XLSX_MIME,
        )
        return {"exportId": export_id}

    def schedule(self, view: str, period: str) -> dict[str, str]:
        """Create a schedule export descriptor for ``view`` / ``period``."""
        view_label = "преподаватели" if view == "teacher" else "группы"
        period_label = "весна" if period == "spring" else "осень"
        export_id = self._new_id()
        self._exports[export_id] = _Export(
            id=export_id,
            file_name=f"расписание_{view_label}_{period_label}.xlsx",
            content=None,
            content_type=_XLSX_MIME,
        )
        return {"exportId": export_id}

    def get(self, export_id: str) -> dict[str, str]:
        """Return a previously issued export descriptor."""
        export = self._require(self._exports.get(export_id), "Экспорт не найден")
        return {"id": export.id, "status": "done", "fileName": export.file_name}

    def download(self, export_id: str) -> tuple[bytes, str, str]:
        """Return the ``(content, filename, content_type)`` for a ready export."""
        export = self._require(self._exports.get(export_id), "Экспорт не найден")
        if export.content is None:
            raise ApiError(404, "Файл экспорта ещё не сформирован")
        return export.content, export.file_name, export.content_type

    def _new_id(self) -> str:
        self._counter += 1
        return f"ex{self._counter}"


def _period_suffix(period: str) -> str:
    """Filename suffix distinguishing the exported season."""
    if period == "fall":
        return "_осень"
    if period == "spring":
        return "_весна"
    return ""


def _year_label(aut_from: str) -> str:
    """Build a ``"2026-2027"`` span from an autumn start date ``dd.mm.yyyy``."""
    try:
        start = int(aut_from.split(".")[-1])
    except (ValueError, IndexError):
        return aut_from
    return f"{start}-{start + 1}"
