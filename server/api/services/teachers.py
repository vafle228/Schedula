"""Application service for teacher resources (profile, photo, constraints)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from api.errors import ApiError
from api.services import ids
from api.services.base import ServiceBase
from core.models.teacher import Teacher, TeacherConstraints
from core.repositories.assignment_repository import AssignmentRepository
from core.repositories.lesson_repository import LessonRepository
from core.repositories.teacher_repository import TeacherRepository


class TeacherService(ServiceBase):
    """List, create, patch and delete teachers and their settings."""

    def __init__(
        self,
        teachers: TeacherRepository,
        assignments: AssignmentRepository,
        lessons: LessonRepository,
    ) -> None:
        self._teachers = teachers
        self._assignments = assignments
        self._lessons = lessons

    def list_all(self) -> list[Teacher]:
        """Return every teacher."""
        return self._teachers.list_all()

    def create(self, name: str, photo: str | None) -> Teacher:
        """Create a teacher with no constraints or absences."""
        teacher = Teacher(
            id=ids.timestamp_id("nt"), name=name,
            photo=photo, constraints=None, absences=[],
        )
        self._teachers.add(teacher)
        return teacher

    def patch(self, teacher_id: str, changes: Mapping[str, Any]) -> Teacher:
        """Apply ``changes`` (currently the name) to a teacher."""
        teacher = self._get(teacher_id)
        self._apply(teacher, changes)
        self._teachers.update(teacher)
        return teacher

    def delete(self, teacher_id: str) -> None:
        """Delete a teacher, refusing while assignments or lessons remain.

        Raises:
            ApiError: ``404`` when missing, ``409`` when still referenced.
        """
        self._get(teacher_id)
        assigned = any(
            a.teacher_id == teacher_id
            for a in self._assignments.get_all().values()
        )
        has_lesson = any(l.teacher_id == teacher_id for l in self._lessons.list_all())
        if assigned or has_lesson:
            raise ApiError(409, "На преподавателя есть назначения или занятия")
        self._teachers.delete(teacher_id)

    def set_photo(self, teacher_id: str, photo: str | None) -> Teacher:
        """Set (or clear with ``None``) a teacher's photo."""
        teacher = self._get(teacher_id)
        teacher.photo = photo
        self._teachers.update(teacher)
        return teacher

    def set_constraints(
        self,
        teacher_id: str,
        *,
        hard: Sequence[str],
        soft: Sequence[str],
        method: int | None,
        max_per_day: int | None,
    ) -> Teacher:
        """Replace a teacher's scheduling constraints."""
        teacher = self._get(teacher_id)
        teacher.constraints = TeacherConstraints(
            hard=list(hard), soft=list(soft), method=method, max_per_day=max_per_day,
        )
        self._teachers.update(teacher)
        return teacher

    def _get(self, teacher_id: str) -> Teacher:
        return self._require(self._teachers.get(teacher_id), "Преподаватель не найден")
