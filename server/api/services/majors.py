"""Application service for major (specialty) resources."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from core.models.major import Major
from core.repositories.group_repository import GroupRepository
from core.repositories.major_repository import MajorRepository


class MajorService(ServiceBase):
    """List, create, patch and delete specialties."""

    def __init__(self, majors: MajorRepository, groups: GroupRepository) -> None:
        self._majors = majors
        self._groups = groups

    def list_with_counts(self) -> list[tuple[Major, int]]:
        """Return every major paired with the number of groups under it."""
        groups = self._groups.list_all()
        return [
            (major, sum(1 for g in groups if g.major_id == major.id))
            for major in self._majors.list_all()
        ]

    def create(self, code: str, name: str) -> Major:
        """Create a new specialty."""
        major = Major(id=0, code=code, name=name)
        self._majors.add(major)
        return major

    def patch(self, major_id: int, changes: Mapping[str, Any]) -> Major:
        """Apply ``changes`` to an existing specialty."""
        major = self._require(self._majors.get(major_id), "Специальность не найдена")
        self._apply(major, changes)
        self._majors.update(major)
        return major

    def delete(self, major_id: int) -> None:
        """Delete a specialty, refusing while it still owns groups.

        Raises:
            ApiError: ``409`` when groups still reference the major.
        """
        if self._groups.list_by_major(major_id):
            raise ApiError(409, "У специальности есть группы")
        self._majors.delete(major_id)
