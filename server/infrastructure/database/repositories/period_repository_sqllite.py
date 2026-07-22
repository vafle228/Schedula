"""SQLite adapter for :class:`PeriodRepository`."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict

from core.models.period import Period, Slot
from core.repositories.period_repository import PeriodRepository


def _row_to_period(row: sqlite3.Row) -> Period:
    return Period(
        id=row["id"],
        date_from=row["date_from"],
        date_to=row["date_to"],
        start_date=row["start_date"],
        active_days=json.loads(row["active_days"]),
        acad_min=row["acad_min"],
        slots=[Slot(**s) for s in json.loads(row["slots"])],
        slots_per_day=row["slots_per_day"],
        weeks_count=row["weeks_count"],
        holidays=json.loads(row["holidays"]),
    )


class PeriodRepositorySqlLite(PeriodRepository):
    """Stores periods with their bell grid and holidays as JSON columns."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[Period]:
        # autumn before spring, matching GET /periods
        rows = self._conn.execute(
            "SELECT * FROM periods ORDER BY (id = 'fall') DESC, rowid"
        ).fetchall()
        return [_row_to_period(r) for r in rows]

    def get(self, period_id: str) -> Period | None:
        row = self._conn.execute(
            "SELECT * FROM periods WHERE id = ?", (period_id,)
        ).fetchone()
        return _row_to_period(row) if row else None

    def save(self, period: Period) -> None:
        self._conn.execute(
            """
            INSERT INTO periods (id, date_from, date_to, start_date, active_days,
                                 acad_min, slots, slots_per_day, weeks_count, holidays)
            VALUES (:id, :date_from, :date_to, :start_date, :active_days,
                    :acad_min, :slots, :slots_per_day, :weeks_count, :holidays)
            ON CONFLICT(id) DO UPDATE SET
                date_from = excluded.date_from,
                date_to = excluded.date_to,
                start_date = excluded.start_date,
                active_days = excluded.active_days,
                acad_min = excluded.acad_min,
                slots = excluded.slots,
                slots_per_day = excluded.slots_per_day,
                weeks_count = excluded.weeks_count,
                holidays = excluded.holidays
            """,
            {
                "id": period.id,
                "date_from": period.date_from,
                "date_to": period.date_to,
                "start_date": period.start_date,
                "active_days": json.dumps(period.active_days),
                "acad_min": period.acad_min,
                "slots": json.dumps([asdict(s) for s in period.slots]),
                "slots_per_day": period.slots_per_day,
                "weeks_count": period.weeks_count,
                "holidays": json.dumps(period.holidays),
            },
        )
        self._conn.commit()
