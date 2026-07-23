"""Application service for topic/teacher assignment resources."""

from __future__ import annotations

from collections.abc import Sequence

from api.services.base import ServiceBase
from api.services.sync import LessonSyncService
from core.models.assignment import Assignment
from core.repositories.assignment_repository import AssignmentRepository, Key
from core.repositories.discipline_repository import DisciplineRepository


class AssignmentService(ServiceBase):
    """Read and mutate the (group, topic)-to-teacher assignment map."""

    def __init__(
        self,
        assignments: AssignmentRepository,
        disciplines: DisciplineRepository,
        sync: LessonSyncService,
    ) -> None:
        self._assignments = assignments
        self._disciplines = disciplines
        self._sync = sync

    def list_by_year(self, year_id: int) -> dict[Key, Assignment]:
        """Return the year's ``(group_id, topic_id) -> Assignment`` map."""
        return self._assignments.list_by_year(year_id)

    def set(
        self, group_id: int, topic_id: int, teacher_id: int | None
    ) -> Assignment | None:
        """Assign (or clear with ``None``) a group's topic and return the result."""
        self._sync.set_assignment(group_id, topic_id, teacher_id)
        return self._assignments.get(group_id, topic_id)

    def clear(self, group_id: int, topic_id: int) -> None:
        """Remove a group's topic assignment and reconcile its lessons."""
        self._sync.set_assignment(group_id, topic_id, None)

    def assign_discipline(
        self, group_id: int, discipline_id: int, teacher_id: int | None
    ) -> list[int]:
        """Assign every still-unassigned topic of a discipline to one group.

        Returns:
            The ids of the topics that were touched.

        Raises:
            ApiError: ``404`` when the discipline does not exist.
        """
        discipline = self._require(
            self._disciplines.get(discipline_id), "Дисциплина не найдена"
        )
        touched: list[int] = []
        for topic in discipline.topics:
            if self._assignments.get(group_id, topic.id) is None:
                self._sync.set_assignment(group_id, topic.id, teacher_id)
                touched.append(topic.id)
        return touched

    def batch(
        self, year_id: int, ops: Sequence[tuple[int, int, int | None]]
    ) -> dict[Key, Assignment]:
        """Apply ``(group_id, topic_id, teacher_id)`` operations for one year."""
        for group_id, topic_id, teacher_id in ops:
            self._sync.set_assignment(group_id, topic_id, teacher_id)
        return self._assignments.list_by_year(year_id)
