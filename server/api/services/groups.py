"""Application service for study-group resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.group import Group
from core.repositories.discipline_repository import DisciplineRepository
from core.repositories.group_repository import GroupRepository
from core.repositories.lesson_repository import LessonRepository
from core.repositories.major_repository import MajorRepository


class GroupService(ServiceBase):
    """List, create, patch and delete study groups."""

    def __init__(
        self,
        groups: GroupRepository,
        majors: MajorRepository,
        disciplines: DisciplineRepository,
        lessons: LessonRepository,
    ) -> None:
        self._groups = groups
        self._majors = majors
        self._disciplines = disciplines
        self._lessons = lessons

    def list_all(self) -> list[Group]:
        """Return every group."""
        return self._groups.list_all()

    def list_by_major(self, major_id: str) -> list[Group]:
        """Return the groups of a single specialty."""
        return self._groups.list_by_major(major_id)

    def create(self, major_id: str, name: str, course: int) -> Group:
        """Create a group under ``major_id``.

        Raises:
            ApiError: ``404`` when the major is missing, ``409`` on a name clash.
        """
        self._require(self._majors.get(major_id), "Специальность не найдена")
        if any(g.id.lower() == name.lower() for g in self._groups.list_all()):
            raise ApiError(409, "Имя группы занято")
        group = Group(id=name, major_id=major_id, course=course)
        self._groups.add(group)
        return group

    def patch(self, group_id: str, changes: Mapping[str, Any]) -> Group:
        """Apply ``changes`` to an existing group."""
        group = self._require(self._groups.get(group_id), "Группа не найдена")
        self._apply(group, changes)
        self._groups.update(group)
        return group

    def delete(self, group_id: str) -> None:
        """Delete a group, refusing while disciplines or lessons reference it.

        Raises:
            ApiError: ``409`` when the group still has disciplines or lessons.
        """
        has_disc = any(d.group_id == group_id for d in self._disciplines.list_all())
        has_lesson = any(l.group_id == group_id for l in self._lessons.list_all())
        if has_disc or has_lesson:
            raise ApiError(409, "У группы есть дисциплины или занятия")
        self._groups.delete(group_id)
