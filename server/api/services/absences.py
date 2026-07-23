"""Application service for teacher absence resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.services import ids
from api.services.base import ServiceBase
from core.models.teacher import Absence, AbsenceType
from core.repositories.absence_repository import AbsenceRepository
from core.repositories.teacher_repository import TeacherRepository


class AbsenceService(ServiceBase):
    """Create, patch and delete the absence periods of a teacher."""

    def __init__(
        self, absences: AbsenceRepository, teachers: TeacherRepository
    ) -> None:
        self._absences = absences
        self._teachers = teachers

    def create(self, teacher_id: str, absence_type: AbsenceType, label: str) -> Absence:
        """Create an absence for ``teacher_id``.

        Raises:
            ApiError: ``404`` when the teacher does not exist.
        """
        self._require(self._teachers.get(teacher_id), "Преподаватель не найден")
        absence = Absence(
            id=ids.next_absence_id(self._teachers),
            teacher_id=teacher_id, type=absence_type, label=label,
        )
        self._absences.add(absence)
        return absence

    def patch(self, absence_id: str, changes: Mapping[str, Any]) -> Absence:
        """Apply ``changes`` to an existing absence."""
        absence = self._require(
            self._absences.get(absence_id), "Период отсутствия не найден"
        )
        self._apply(absence, changes)
        self._absences.update(absence)
        return absence

    def delete(self, absence_id: str) -> None:
        """Delete an absence (no-op if it is already gone)."""
        self._absences.delete(absence_id)
