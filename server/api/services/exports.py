"""Application service for export (curriculum/schedule download) resources.

Mirrors the mock's ``db.exports``: descriptors are issued and read back but
never persisted, so they live in memory on the service instance.
"""

from __future__ import annotations

from api.services.base import ServiceBase


class ExportService(ServiceBase):
    """Issues export descriptors (curriculum / schedule)."""

    def __init__(self) -> None:
        self._exports: dict[str, dict[str, str]] = {}
        self._counter = 0

    def curriculum(self, period: str) -> dict[str, str]:
        """Create a curriculum export descriptor for ``period``."""
        export_id = self._new_id()
        suffix = "" if period == "both" else ("_осень" if period == "fall" else "_весна")
        self._exports[export_id] = {
            "id": export_id,
            "status": "done",
            "fileName": f"Учебный_план_2026-27{suffix}.xlsx",
        }
        return {"exportId": export_id}

    def schedule(self, view: str, period: str) -> dict[str, str]:
        """Create a schedule export descriptor for ``view`` / ``period``."""
        export_id = self._new_id()
        view_label = "преподаватели" if view == "teacher" else "группы"
        period_label = "весна" if period == "spring" else "осень"
        self._exports[export_id] = {
            "id": export_id,
            "status": "done",
            "fileName": f"расписание_{view_label}_{period_label}.xlsx",
        }
        return {"exportId": export_id}

    def get(self, export_id: str) -> dict[str, str]:
        """Return a previously issued export descriptor."""
        return self._require(self._exports.get(export_id), "Экспорт не найден")

    def _new_id(self) -> str:
        self._counter += 1
        return f"ex{self._counter}"
