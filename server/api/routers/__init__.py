"""Per-domain route tables and the shared request dispatcher."""

from __future__ import annotations

from api.routers.absences import register_absence_routes
from api.routers.assignments import register_assignment_routes
from api.routers.disciplines import register_discipline_routes
from api.routers.dispatcher import Router
from api.routers.exports import register_export_routes
from api.routers.groups import register_group_routes
from api.routers.lessons import register_lesson_routes
from api.routers.majors import register_major_routes
from api.routers.periods import register_period_routes
from api.routers.rooms import register_room_routes
from api.routers.schedule import register_schedule_routes
from api.routers.teachers import register_teacher_routes
from api.routers.topic_types import register_topic_type_routes
from api.routers.topics import register_topic_routes
from api.routers.years import register_year_routes

__all__ = [
    "Router",
    "register_absence_routes",
    "register_assignment_routes",
    "register_discipline_routes",
    "register_export_routes",
    "register_group_routes",
    "register_lesson_routes",
    "register_major_routes",
    "register_period_routes",
    "register_room_routes",
    "register_schedule_routes",
    "register_teacher_routes",
    "register_topic_routes",
    "register_topic_type_routes",
    "register_year_routes",
]
