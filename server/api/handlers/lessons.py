"""HTTP handlers for lesson (scheduled pair) resources."""

from __future__ import annotations

from typing import Any, Final

from api.http_types import Body, Params, Query
from api.schemas import serialize as ser
from api.services.lessons import LessonService

# Wire (camelCase) → domain (snake_case) attribute names for a lesson.
_LESSON_FIELDS: Final[dict[str, str]] = {
    "topicId": "topic_id", "disciplineId": "discipline_id",
    "groupId": "group_id", "teacherId": "teacher_id", "roomId": "room_id",
    "kind": "kind", "period": "period", "week": "week", "day": "day", "slot": "slot",
    "subBy": "sub_by", "pin": "pin", "manual": "manual", "ni": "ni", "nt": "nt",
    "topicLabel": "topic_label", "question": "question",
}


class LessonHandlers:
    """Translate lesson requests to :class:`LessonService` calls."""

    def __init__(self, service: LessonService) -> None:
        self._service = service

    def list(self, params: Params, query: Query, body: Body) -> list[dict[str, Any]]:
        return [ser.lesson(lesson) for lesson in self._service.list_all()]

    def create(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        return ser.lesson(self._service.create(self._to_attrs(body)))

    def patch(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        assert body is not None
        changes = self._to_attrs(body)
        return ser.lesson(self._service.patch(int(params["id"]), changes))

    def delete(self, params: Params, query: Query, body: Body) -> None:
        self._service.delete(int(params["id"]))
        return None

    def pin(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.lesson(self._service.set_pin(int(params["id"]), True))

    def unpin(self, params: Params, query: Query, body: Body) -> dict[str, Any]:
        return ser.lesson(self._service.set_pin(int(params["id"]), False))

    @staticmethod
    def _to_attrs(body: dict[str, Any]) -> dict[str, Any]:
        return {
            attr: body[camel]
            for camel, attr in _LESSON_FIELDS.items()
            if camel in body
        }
