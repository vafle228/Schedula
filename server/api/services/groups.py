"""Application service for study-group resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.group import Group
from core.repositories.group_repository import GroupRepository
from core.repositories.lesson_repository import LessonRepository
from core.repositories.major_repository import MajorRepository


class GroupService(ServiceBase):
    """List, create, patch and delete study groups."""

    def __init__(
        self,
        groups: GroupRepository,
        majors: MajorRepository,
        lessons: LessonRepository,
    ) -> None:
        self._groups = groups
        self._majors = majors
        self._lessons = lessons

    def list_by_year(self, year_id: int) -> list[Group]:
        """Return the year's groups."""
        return self._groups.list_by_year(year_id)

    def list_by_year_major(self, year_id: int, major_id: int) -> list[Group]:
        """Return the year's groups of a single specialty."""
        return self._groups.list_by_year_major(year_id, major_id)

    def create(self, year_id: int, major_id: int, name: str, course: int) -> Group:
        """Create a group under ``major_id`` in ``year_id``.

        Raises:
            ApiError: ``404`` when the major is missing, ``409`` on a name clash
                within the same year.
        """
        self._require(self._majors.get(major_id), "Специальность не найдена")
        existing = self._groups.list_by_year(year_id)
        if any(g.name.lower() == name.lower() for g in existing):
            raise ApiError(409, "Имя группы занято")
        group = Group(id=0, year_id=year_id, name=name, major_id=major_id, course=course)
        self._groups.add(group)
        return group

    def patch(self, group_id: int, changes: Mapping[str, Any]) -> Group:
        """Apply ``changes`` to an existing group."""
        group = self._require(self._groups.get(group_id), "Группа не найдена")
        self._apply(group, changes)
        self._groups.update(group)
        return group

    def delete(self, group_id: int) -> None:
        """Delete a group, refusing while its lessons still exist.

        Disciplines are shared per major and course, so they never block a
        single group's removal; the group's assignments cascade off its FK.

        Raises:
            ApiError: ``404`` when missing, ``409`` when the group still has
                lessons.
        """
        group = self._require(self._groups.get(group_id), "Группа не найдена")
        has_lesson = any(
            l.group_id == group_id
            for l in self._lessons.list_by_year(group.year_id)
        )
        if has_lesson:
            raise ApiError(409, "У группы есть занятия")
        self._groups.delete(group_id)
