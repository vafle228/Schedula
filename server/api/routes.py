"""Composition root for the HTTP layer.

Wires the four layers together for every domain — ``router -> handler ->
service -> repository`` — and exposes the resulting ``dispatch`` callable.
Services depend only on the abstract repository ports, so the concrete
:class:`SqliteUnitOfWork` is injected here and nowhere deeper. ``main.py`` feeds
the dispatcher ``(method, url, body)`` and serializes the result; the route
patterns mirror the client's mock ``server.js`` so the wire contract stays
byte-identical.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from api.handlers import (
    AbsenceHandlers,
    AssignmentHandlers,
    DisciplineHandlers,
    ExportHandlers,
    GroupHandlers,
    LessonHandlers,
    MajorHandlers,
    RoomHandlers,
    ScheduleHandlers,
    SettingsHandlers,
    TeacherHandlers,
    TopicHandlers,
    TopicTypeHandlers,
    YearHandlers,
)
from api.routers import (
    Router,
    register_absence_routes,
    register_assignment_routes,
    register_discipline_routes,
    register_export_routes,
    register_group_routes,
    register_lesson_routes,
    register_major_routes,
    register_room_routes,
    register_schedule_routes,
    register_settings_routes,
    register_teacher_routes,
    register_topic_routes,
    register_topic_type_routes,
    register_year_routes,
)
from api.services import (
    AbsenceService,
    AssignmentService,
    DisciplineService,
    ExportService,
    GroupService,
    LessonService,
    LessonSyncService,
    MajorService,
    RolloverService,
    RoomService,
    ScheduleService,
    SettingsService,
    TeacherService,
    TopicService,
    TopicTypeService,
    YearService,
)
from infrastructure.database.unit_of_work import SqliteUnitOfWork


def create_dispatcher(
    uow: SqliteUnitOfWork,
) -> Callable[[str, str, dict[str, Any] | None], Any]:
    """Build the request dispatcher bound to a unit of work.

    Args:
        uow: The persistence composition root exposing the concrete
            repositories that satisfy the abstract ports the services need.

    Returns:
        ``dispatch(method, url, body)`` returning the (json-serializable)
        result, or ``None`` for 204. Handlers surface
        :class:`api.errors.ApiError` for 4xx.
    """
    sync = LessonSyncService(
        topics=uow.topics,
        disciplines=uow.disciplines,
        groups=uow.groups,
        assignments=uow.assignments,
        settings=uow.settings,
        lessons=uow.lessons,
        rooms=uow.rooms,
        teachers=uow.teachers,
    )

    router = Router()
    register_settings_routes(
        router, SettingsHandlers(SettingsService(uow.settings, uow.years))
    )
    register_year_routes(
        router,
        YearHandlers(
            YearService(uow.years, uow.settings, uow.lessons),
            RolloverService(years=uow.years, disciplines=uow.disciplines),
        ),
    )
    register_topic_type_routes(
        router,
        TopicTypeHandlers(TopicTypeService(uow.topic_types, uow.disciplines)),
    )
    register_major_routes(
        router, MajorHandlers(MajorService(uow.majors, uow.groups))
    )
    register_group_routes(
        router,
        GroupHandlers(GroupService(uow.groups, uow.majors, uow.lessons)),
    )
    register_discipline_routes(
        router,
        DisciplineHandlers(
            DisciplineService(uow.disciplines, uow.topics, uow.lessons)
        ),
    )
    register_topic_routes(
        router,
        TopicHandlers(
            TopicService(uow.topics, uow.disciplines, uow.lessons, sync)
        ),
    )
    register_assignment_routes(
        router,
        AssignmentHandlers(
            AssignmentService(uow.assignments, uow.disciplines, sync)
        ),
    )
    register_teacher_routes(
        router,
        TeacherHandlers(
            TeacherService(uow.teachers, uow.assignments, uow.lessons)
        ),
    )
    register_absence_routes(
        router, AbsenceHandlers(AbsenceService(uow.absences, uow.teachers))
    )
    register_room_routes(
        router, RoomHandlers(RoomService(uow.rooms, uow.lessons))
    )
    register_lesson_routes(
        router, LessonHandlers(LessonService(uow.lessons, uow.topics))
    )
    register_schedule_routes(
        router,
        ScheduleHandlers(
            ScheduleService(
                lessons=uow.lessons,
                teachers=uow.teachers,
                rooms=uow.rooms,
                settings=uow.settings,
                topic_types=uow.topic_types,
                sync=sync,
            )
        ),
    )
    register_export_routes(router, ExportHandlers(ExportService()))

    return router.dispatch
