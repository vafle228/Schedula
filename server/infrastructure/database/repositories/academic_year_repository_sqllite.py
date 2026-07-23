"""SQLite adapter for :class:`AcademicYearRepository`."""

from __future__ import annotations

import sqlite3

from core.models.academic_year import AcademicYear, YearStatus
from core.repositories.academic_year_repository import AcademicYearRepository


def _row_to_year(row: sqlite3.Row) -> AcademicYear:
    return AcademicYear(
        id=row["id"],
        name=row["name"],
        aut_from=row["aut_from"],
        aut_to=row["aut_to"],
        spr_from=row["spr_from"],
        spr_to=row["spr_to"],
        status=YearStatus(row["status"]),
    )


class AcademicYearRepositorySqlLite(AcademicYearRepository):
    """Stores academic years, preserving insertion order via ``rowid``."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def list_all(self) -> list[AcademicYear]:
        rows = self._conn.execute(
            "SELECT * FROM academic_years ORDER BY rowid"
        ).fetchall()
        return [_row_to_year(r) for r in rows]

    def get(self, year_id: int) -> AcademicYear | None:
        row = self._conn.execute(
            "SELECT * FROM academic_years WHERE id = ?", (year_id,)
        ).fetchone()
        return _row_to_year(row) if row else None

    def add(self, year: AcademicYear) -> int:
        cursor = self._conn.execute(
            """
            INSERT INTO academic_years (name, aut_from, aut_to, spr_from, spr_to, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                year.name,
                year.aut_from,
                year.aut_to,
                year.spr_from,
                year.spr_to,
                str(year.status),
            ),
        )
        self._conn.commit()
        year.id = cursor.lastrowid
        return year.id

    def update(self, year: AcademicYear) -> None:
        self._conn.execute(
            """
            UPDATE academic_years
               SET name = ?, aut_from = ?, aut_to = ?, spr_from = ?,
                   spr_to = ?, status = ?
             WHERE id = ?
            """,
            (
                year.name,
                year.aut_from,
                year.aut_to,
                year.spr_from,
                year.spr_to,
                str(year.status),
                year.id,
            ),
        )
        self._conn.commit()

    def delete(self, year_id: int) -> None:
        self._conn.execute("DELETE FROM academic_years WHERE id = ?", (year_id,))
        self._conn.commit()
