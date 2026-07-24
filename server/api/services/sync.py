"""Lesson-graph synchronisation — a faithful port of the client's ``sync.js``.

Reconciles the auto-generated lesson slots of a topic with its assignment
state and builds the flat lesson views the schedule engine consumes. Shared by
the topic, assignment and schedule services as an injected collaborator.

Rules:
  - an assigned topic owns ``pairs_per_week`` lesson slots (auto = hours ÷ 2 ÷
    weeks);
  - unassigning drops pool pairs but keeps already-placed ones as orphans;
  - reassigning moves every pair of the topic to the new teacher.
"""

from __future__ import annotations

import math

from api.services.base import ServiceBase
from api.services.conflicts import EnrichedLesson
from core.models.assignment import Assignment
from core.models.discipline import Discipline, Topic
from core.models.lesson import Lesson
from core.models.settings import SemesterSettings
from core.repositories.assignment_repository import AssignmentRepository
from core.repositories.discipline_repository import (
    DisciplineRepository,
    TopicRepository,
)
from core.repositories.group_repository import GroupRepository
from core.repositories.lesson_repository import LessonRepository
from core.repositories.room_repository import RoomRepository
from core.repositories.settings_repository import SettingsRepository
from core.repositories.teacher_repository import TeacherRepository


class LessonSyncService(ServiceBase):
    """Keeps a topic's auto lessons and assignment in step, and enriches views."""

    def __init__(
        self,
        *,
        topics: TopicRepository,
        disciplines: DisciplineRepository,
        groups: GroupRepository,
        assignments: AssignmentRepository,
        settings: SettingsRepository,
        lessons: LessonRepository,
        rooms: RoomRepository,
        teachers: TeacherRepository,
    ) -> None:
        self._topics = topics
        self._disciplines = disciplines
        self._groups = groups
        self._assignments = assignments
        self._settings = settings
        self._lessons = lessons
        self._rooms = rooms
        self._teachers = teachers

    @staticmethod
    def pairs_per_week(topic: Topic, settings: SemesterSettings) -> int:
        """Weekly pair count a topic materialises (``max(1, round(h/2/weeks))``)."""
        weeks = settings.weeks_count or 16
        return max(1, math.floor(topic.hours / 2 / weeks + 0.5))

    def set_assignment(
        self, group_id: int, topic_id: int, teacher_id: int | None
    ) -> None:
        """Assign (or clear with ``None``) a group's topic teacher, then reconcile.

        Raises:
            ApiError: 404 when the topic or teacher does not exist.
        """
        topic = self._require(self._topics.get(topic_id), "Тема не найдена")

        if teacher_id is None:
            self._assignments.delete(group_id, topic_id)
        else:
            self._require(
                self._teachers.get(teacher_id), "Преподаватель не найден"
            )
            discipline = self._disciplines.get(topic.discipline_id)
            settings = self._settings.get(discipline.year_id, discipline.period)
            self._assignments.set(Assignment(
                group_id, topic_id, teacher_id, self.pairs_per_week(topic, settings)
            ))

        self._sync_pair(group_id, topic_id)

    def sync_topic(self, topic_id: int) -> None:
        """Reconcile every group's auto lessons after the topic itself changed.

        Re-syncs each group that has an assignment on the topic (e.g. after its
        hours changed). Pairs without an assignment keep their placed lessons as
        orphans and need no reconciliation here.
        """
        for assignment in self._assignments.list_by_topic(topic_id):
            self._sync_pair(assignment.group_id, topic_id)

    def _sync_pair(self, group_id: int, topic_id: int) -> None:
        """Reconcile one group's auto lessons for a topic with its assignment."""
        topic = self._topics.get(topic_id)
        discipline = self._disciplines.get(topic.discipline_id) if topic else None
        assignment = self._assignments.get(group_id, topic_id)

        if topic is None or discipline is None or assignment is None:
            # topic gone or unassigned: pool pairs disappear, placed ones orphan
            for lesson in self._lessons.list_by_group_topic(group_id, topic_id):
                if not (topic is not None and lesson.day is not None):
                    self._lessons.delete(lesson.id)
            return

        settings = self._settings.get(discipline.year_id, discipline.period)
        target_pairs = self.pairs_per_week(topic, settings)
        assignment.pairs_per_week = target_pairs
        self._assignments.set(assignment)

        own = self._lessons.list_by_group_topic(group_id, topic_id)
        for lesson in own:
            lesson.teacher_id = assignment.teacher_id
            lesson.period = discipline.period
            self._lessons.update(lesson)

        auto = [l for l in own if not l.manual]
        placed_n = len([l for l in auto if l.day is not None])
        target = max(target_pairs, placed_n)

        surplus = len(auto) - target
        if surplus > 0:
            pool = [l for l in auto if l.day is None]
            for lesson in pool[-surplus:]:
                self._lessons.delete(lesson.id)

        have = len([
            l for l in self._lessons.list_by_group_topic(group_id, topic_id)
            if not l.manual
        ])
        for _ in range(have, target):
            lesson = Lesson(
                id=0,
                year_id=discipline.year_id,
                topic_id=topic_id,
                discipline_id=discipline.id,
                group_id=group_id,
                teacher_id=assignment.teacher_id,
                room_id=self._default_room(topic, discipline, group_id),
                kind=topic.kind,
                period=discipline.period,
                week=None, day=None, slot=None, sub_by=None,
                manual=False, ni=0, nt=target,
                topic_label="", question="",
            )
            self._lessons.add(lesson)

        ni = 0
        for lesson in self._lessons.list_by_group_topic(group_id, topic_id):
            if not lesson.manual:
                ni += 1
                lesson.ni = ni
                lesson.nt = target
                self._lessons.update(lesson)

    def enrich(self, year_id: int, period: str) -> list[EnrichedLesson]:
        """Build the flat lesson views for the generator / conflict engine."""
        disc_names = {d.id: d.name for d in self._disciplines.list_by_year(year_id)}
        group_names = {g.id: g.name for g in self._groups.list_by_year(year_id)}
        assignments = self._assignments.list_by_year(year_id)
        return [
            EnrichedLesson(
                id=lesson.id,
                g=group_names.get(lesson.group_id, str(lesson.group_id)),
                disc=disc_names.get(lesson.discipline_id, ""),
                t=lesson.teacher_id,
                room=lesson.room_id,
                kind=lesson.kind,
                w=lesson.week,
                d=lesson.day,
                s=lesson.slot,
                sub_by=lesson.sub_by,
                orphan=(lesson.group_id, lesson.topic_id) not in assignments,
                number=lesson.number,
            )
            for lesson in self._lessons.list_by_year_period(year_id, period)
        ]

    def _default_room(
        self, topic: Topic, discipline: Discipline, group_id: int
    ) -> str:
        """Pick a room for a fresh pool lesson: reuse a sibling's, else by kind."""
        for lesson in self._lessons.list_by_year(discipline.year_id):
            if (
                lesson.group_id == group_id
                and lesson.discipline_id == discipline.id
                and lesson.room_id
            ):
                return lesson.room_id
        wanted = "Комп. класс" if topic.kind == "prac" else "Лекционная"
        rooms = self._rooms.list_all()
        for room in rooms:
            if room.type == wanted:
                return room.id
        return rooms[0].id if rooms else ""
