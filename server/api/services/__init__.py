"""Application service classes, grouped one module per domain entity.

Each service depends only on the abstract repository ports from
:mod:`core.repositories` (dependency inversion) and holds the business rules
that sit between the HTTP handlers and persistence:
``router -> handler -> service -> repository``.
"""

from __future__ import annotations

from api.services.absences import AbsenceService
from api.services.assignments import AssignmentService
from api.services.disciplines import DisciplineService
from api.services.exports import ExportService
from api.services.groups import GroupService
from api.services.lessons import LessonService
from api.services.majors import MajorService
from api.services.periods import PeriodService
from api.services.rooms import RoomService
from api.services.schedule import ScheduleService
from api.services.sync import LessonSyncService
from api.services.teachers import TeacherService
from api.services.topic_types import TopicTypeService
from api.services.topics import TopicService
from api.services.years import YearService

__all__ = [
    "AbsenceService",
    "AssignmentService",
    "DisciplineService",
    "ExportService",
    "GroupService",
    "LessonService",
    "LessonSyncService",
    "MajorService",
    "PeriodService",
    "RoomService",
    "ScheduleService",
    "TeacherService",
    "TopicService",
    "TopicTypeService",
    "YearService",
]
