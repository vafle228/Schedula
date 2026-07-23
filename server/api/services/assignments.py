"""Application service for topic/teacher assignment resources."""

from __future__ import annotations

from collections.abc import Sequence

from api.services.base import ServiceBase
from api.services.sync import LessonSyncService
from core.models.assignment import Assignment
from core.repositories.assignment_repository import AssignmentRepository
from core.repositories.discipline_repository import DisciplineRepository


class AssignmentService(ServiceBase):
    """Read and mutate the topic-to-teacher assignment map."""

    def __init__(
        self,
        assignments: AssignmentRepository,
        disciplines: DisciplineRepository,
        sync: LessonSyncService,
    ) -> None:
        self._assignments = assignments
        self._disciplines = disciplines
        self._sync = sync

    def list_all(self) -> dict[int, Assignment]:
        """Return the full ``topic_id -> Assignment`` map."""
        return self._assignments.get_all()

    def set(self, topic_id: int, teacher_id: int | None) -> Assignment | None:
        """Assign (or clear with ``None``) a topic and return the result."""
        self._sync.set_assignment(topic_id, teacher_id)
        return self._assignments.get(topic_id)

    def clear(self, topic_id: int) -> None:
        """Remove a topic's assignment and reconcile its lessons."""
        self._sync.set_assignment(topic_id, None)

    def assign_discipline(
        self, discipline_id: int, teacher_id: int | None
    ) -> list[int]:
        """Assign every still-unassigned topic of a discipline to a teacher.

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
            if self._assignments.get(topic.id) is None:
                self._sync.set_assignment(topic.id, teacher_id)
                touched.append(topic.id)
        return touched

    def batch(
        self, ops: Sequence[tuple[int, int | None]]
    ) -> dict[int, Assignment]:
        """Apply a batch of ``(topic_id, teacher_id)`` operations."""
        for topic_id, teacher_id in ops:
            self._sync.set_assignment(topic_id, teacher_id)
        return self._assignments.get_all()
