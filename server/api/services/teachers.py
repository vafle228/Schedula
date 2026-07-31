"""Application service for teacher resources (profile, photo, constraints)."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from api.services.images import PhotoError, PhotoTooLargeError, encode_photo
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
        """Create a teacher with no constraints or absences.

        Args:
            name: Display name.
            photo: Raw upload (``data:`` URL or base64), or ``None``.

        Raises:
            ApiError: ``400``/``413`` when the photo cannot be stored.
        """
        teacher = Teacher(
            id=0,
            name=name,
            photo=self._encode_photo(photo),
            constraints=None,
            absences=[],
        )
        self._teachers.add(teacher)
        return teacher

    def patch(self, teacher_id: int, changes: Mapping[str, Any]) -> Teacher:
        """Apply ``changes`` (currently the name) to a teacher."""
        teacher = self._get(teacher_id)
        self._apply(teacher, changes)
        self._teachers.update(teacher)
        return teacher

    def delete(self, teacher_id: int) -> None:
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

    def set_photo(self, teacher_id: int, photo: str | None) -> Teacher:
        """Set (or clear with ``None``) a teacher's photo.

        Args:
            teacher_id: Target teacher.
            photo: Raw upload (``data:`` URL or base64); ``None`` clears it.

        Raises:
            ApiError: ``404`` when missing, ``400``/``413`` on a bad photo.
        """
        teacher = self._get(teacher_id)
        teacher.photo = self._encode_photo(photo)
        self._teachers.update(teacher)
        return teacher

    def set_constraints(
        self,
        teacher_id: int,
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

    def _get(self, teacher_id: int) -> Teacher:
        return self._require(self._teachers.get(teacher_id), "Преподаватель не найден")

    @staticmethod
    def _encode_photo(photo: str | None) -> str | None:
        """Normalise an upload to the stored JPEG payload, or pass ``None`` on.

        Raises:
            ApiError: ``413`` when the file is too large, ``400`` when it is not
                a readable image.
        """
        if not photo:
            return None
        try:
            return encode_photo(photo)
        except PhotoTooLargeError as err:
            raise ApiError(413, "Файл слишком большой — максимум 12 МБ") from err
        except PhotoError as err:
            raise ApiError(400, "Не удалось обработать изображение") from err
