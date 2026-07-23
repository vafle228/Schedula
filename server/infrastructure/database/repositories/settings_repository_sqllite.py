"""SQLite adapter for :class:`SettingsRepository`."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict

from core.models.settings import SemesterSettings, Slot
from core.repositories.settings_repository import SettingsRepository


def _row_to_settings(row: sqlite3.Row) -> SemesterSettings:
    return SemesterSettings(
        year_id=row["year_id"],
        period=row["period"],
        start_date=row["start_date"],
        active_days=json.loads(row["active_days"]),
        acad_min=row["acad_min"],
        slots=[Slot(**s) for s in json.loads(row["slots"])],
        slots_per_day=row["slots_per_day"],
        weeks_count=row["weeks_count"],
        holidays=json.loads(row["holidays"]),
    )


class SettingsRepositorySqlLite(SettingsRepository):
    """Stores per-year semester settings with their bell grid as JSON columns."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_by_year(self, year_id: int) -> list[SemesterSettings]:
        # autumn before spring, matching the client's expected order
        rows = self._conn.execute(
            "SELECT * FROM settings WHERE year_id = ? "
            "ORDER BY (period = 'fall') DESC, rowid",
            (year_id,),
        ).fetchall()
        return [_row_to_settings(r) for r in rows]

    def get(self, year_id: int, period: str) -> SemesterSettings | None:
        row = self._conn.execute(
            "SELECT * FROM settings WHERE year_id = ? AND period = ?",
            (year_id, period),
        ).fetchone()
        return _row_to_settings(row) if row else None

    def save(self, settings: SemesterSettings) -> None:
        self._conn.execute(
            """
            INSERT INTO settings (year_id, period, start_date, active_days,
                                  acad_min, slots, slots_per_day, weeks_count, holidays)
            VALUES (:year_id, :period, :start_date, :active_days,
                    :acad_min, :slots, :slots_per_day, :weeks_count, :holidays)
            ON CONFLICT(year_id, period) DO UPDATE SET
                start_date = excluded.start_date,
                active_days = excluded.active_days,
                acad_min = excluded.acad_min,
                slots = excluded.slots,
                slots_per_day = excluded.slots_per_day,
                weeks_count = excluded.weeks_count,
                holidays = excluded.holidays
            """,
            {
                "year_id": settings.year_id,
                "period": settings.period,
                "start_date": settings.start_date,
                "active_days": json.dumps(settings.active_days),
                "acad_min": settings.acad_min,
                "slots": json.dumps([asdict(s) for s in settings.slots]),
                "slots_per_day": settings.slots_per_day,
                "weeks_count": settings.weeks_count,
                "holidays": json.dumps(settings.holidays),
            },
        )
        self._conn.commit()

    def delete_for_year(self, year_id: int) -> None:
        self._conn.execute("DELETE FROM settings WHERE year_id = ?", (year_id,))
        self._conn.commit()
