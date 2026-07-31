"""SQLite adapter for :class:`WorkspaceRepository`."""

from __future__ import annotations

import sqlite3

from core.repositories.workspace_repository import WorkspaceRepository
from infrastructure.database.connection import transaction

_COUNTED_TABLES: tuple[str, ...] = (
    "academic_years",
    "majors",
    "groups",
    "teachers",
    "absences",
    "rooms",
    "disciplines",
    "topics",
    "assignments",
    "lessons",
)

# Child rows first: PRAGMA foreign_keys is ON, ``lessons.year_id`` has no
# REFERENCES clause (so no cascade fires for it) and the ``major_id`` columns
# are NO ACTION, which would refuse a majors-first delete.
_PURGE_ORDER: tuple[str, ...] = (
    "lessons",
    "assignments",
    "topics",
    "disciplines",
    "groups",
    "settings",
    "academic_years",
    "absences",
    "teachers",
    "rooms",
    "majors",
)


class WorkspaceRepositorySqlLite(WorkspaceRepository):
    """Counts and clears every user-content table on one connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def counts(self) -> dict[str, int]:
        return {
            table: self._conn.execute(
                f"SELECT COUNT(*) FROM {table}"  # noqa: S608 - fixed identifier list
            ).fetchone()[0]
            for table in _COUNTED_TABLES
        }

    def purge(self) -> None:
        with transaction(self._conn) as conn:
            for table in _PURGE_ORDER:
                conn.execute(f"DELETE FROM {table}")  # noqa: S608 - fixed list
