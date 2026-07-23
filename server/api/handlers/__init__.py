"""Domain HTTP handler classes, grouped one module per entity."""

from __future__ import annotations

from api.handlers.absences import AbsenceHandlers
from api.handlers.assignments import AssignmentHandlers
from api.handlers.disciplines import DisciplineHandlers
from api.handlers.exports import ExportHandlers
from api.handlers.groups import GroupHandlers
from api.handlers.lessons import LessonHandlers
from api.handlers.majors import MajorHandlers
from api.handlers.rooms import RoomHandlers
from api.handlers.schedule import ScheduleHandlers
from api.handlers.settings import SettingsHandlers
from api.handlers.teachers import TeacherHandlers
from api.handlers.topic_types import TopicTypeHandlers
from api.handlers.topics import TopicHandlers
from api.handlers.years import YearHandlers

__all__ = [
    "AbsenceHandlers",
    "AssignmentHandlers",
    "DisciplineHandlers",
    "ExportHandlers",
    "GroupHandlers",
    "LessonHandlers",
    "MajorHandlers",
    "RoomHandlers",
    "ScheduleHandlers",
    "SettingsHandlers",
    "TeacherHandlers",
    "TopicHandlers",
    "TopicTypeHandlers",
    "YearHandlers",
]
