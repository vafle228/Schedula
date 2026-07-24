"""Application service for schedule readiness, generation and conflicts.

Owns the ephemeral generation jobs (render/progress state that the mock keeps
in ``db.jobs`` and that is intentionally *not* persisted) alongside the
readiness report and the conflict pass. The heavy lifting lives in the pure
:mod:`api.services.conflicts` / :mod:`api.services.generator` modules; this
service supplies them with data from the repositories and the injected
:class:`LessonSyncService`.
"""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from api.services.conflicts import analyze
from api.services.generator import compute_generation
from api.services.kinds import make_kind_hours
from api.services.sync import LessonSyncService
from core.repositories.lesson_repository import LessonRepository
from core.repositories.room_repository import RoomRepository
from core.repositories.settings_repository import SettingsRepository
from core.repositories.teacher_repository import TeacherRepository
from core.repositories.topic_type_repository import TopicTypeRepository

_GEN_STAGES = [
    "Готовлю данные…",
    "Размещаю лекции…",
    "Размещаю практики…",
    "Разрешаю конфликты аудиторий…",
    "Проверяю пожелания…",
]


def _mround(value: float) -> int:
    """Round half up, matching JavaScript's ``Math.round``."""
    return int(value + 0.5)


class ScheduleService(ServiceBase):
    """Report readiness, drive generation jobs and surface conflicts."""

    def __init__(
        self,
        *,
        lessons: LessonRepository,
        teachers: TeacherRepository,
        rooms: RoomRepository,
        settings: SettingsRepository,
        topic_types: TopicTypeRepository,
        sync: LessonSyncService,
    ) -> None:
        self._lessons = lessons
        self._teachers = teachers
        self._rooms = rooms
        self._settings = settings
        self._topic_types = topic_types
        self._sync = sync
        self._jobs: dict[str, dict[str, Any]] = {}
        self._counter = 0

    def readiness(self, year_id: int, period: str) -> dict[str, Any]:
        """Summarise how ready the year's ``period`` is for generation."""
        lessons = self._lessons.list_by_year_period(year_id, period)
        return {
            "totalPairs": len(lessons),
            "placedPairs": sum(1 for l in lessons if l.day is not None),
            "noConstraintsTeachers": sum(
                1 for t in self._teachers.list_all() if t.constraints is None
            ),
            "roomsCount": len(self._rooms.list_all()),
        }

    def conflicts(self, year_id: int, period: str) -> dict[str, Any]:
        """Run the conflict pass over a year's ``period`` and return the result."""
        return analyze(
            self._sync.enrich(year_id, period),
            self._teachers.list_all(),
            self._settings.get(year_id, period),
            self._kind_hours(),
        )

    def start_generation(self, year_id: int, period: str, mode: str) -> dict[str, str]:
        """Kick off a generation job and return its id."""
        result = compute_generation(
            self._sync.enrich(year_id, period),
            self._teachers.list_all(),
            self._settings.get(year_id, period),
            mode,
            self._kind_hours(),
        )
        self._counter += 1
        job_id = f"job{self._counter}"
        self._jobs[job_id] = {"pct": 0.0, "stage": 0, "status": "run", "result": result}
        return {"jobId": job_id}

    def generation_status(self, job_id: str) -> dict[str, Any]:
        """Advance and report a job's simulated progress."""
        job = self._job(job_id)
        if job["status"] == "run":
            job["pct"] = min(100.0, job["pct"] + 3 + random.random() * 7)
            job["stage"] = min(len(_GEN_STAGES) - 1, int(job["pct"] // 20))
            if job["pct"] >= 100:
                job["status"] = "done"
        result = job["result"]
        total = result["placedN"] + result["unplacedN"]
        summary = None
        if job["status"] == "done":
            summary = {
                "placedN": result["placedN"],
                "unplacedN": result["unplacedN"],
                "softN": result["softN"],
                "moved": result["moved"],
                "unplaced": result["unplaced"],
            }
        return {
            "status": job["status"],
            "pct": _mround(job["pct"]),
            "stage": _GEN_STAGES[job["stage"]],
            "live": f"размещено {_mround(job['pct'] / 100 * result['placedN'])} / {total}",
            "summary": summary,
        }

    def cancel_generation(self, job_id: str) -> None:
        """Discard a job (cancel or rollback)."""
        self._jobs.pop(job_id, None)

    def accept_generation(self, job_id: str) -> dict[str, list[str]]:
        """Persist a finished job's placements and return the highlighted ids."""
        job = self._job(job_id)
        for placement in job["result"]["placements"]:
            lesson = self._lessons.get(placement["id"])
            if lesson is not None:
                lesson.week = placement["w"]
                lesson.day = placement["d"]
                lesson.slot = placement["s"]
                self._lessons.update(lesson)
        new_ids = job["result"]["newIds"]
        self._jobs.pop(job_id, None)
        return {"newIds": new_ids}

    def _job(self, job_id: str) -> dict[str, Any]:
        job = self._jobs.get(job_id)
        if job is None:
            raise ApiError(404, "Задача не найдена")
        return job

    def _kind_hours(self) -> Callable[[str], int]:
        return make_kind_hours(self._topic_types.list_all())
