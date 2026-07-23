"""Semester settings — the schedule grid definition, scoped per academic year.

Each academic year owns two settings rows, one per season (``fall`` / ``spring``).
A settings row owns the bell grid (``slots``), the active week days, holiday cells
and the number of teaching weeks. Calendar dates (``date_from`` / ``date_to``) are
*not* stored here — they are derived from the parent year at serialization time.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Slot:
    """One bell-grid slot: a start time and how many academic hours it spans.

    Attributes:
        start: Wall-clock start, ``"HH:MM"``.
        hours: Academic hours the slot occupies (1 or 2).
        brk: Break in minutes *after* this slot (unused for the last one).
    """

    start: str
    hours: int
    brk: int


@dataclass(slots=True)
class SemesterSettings:
    """Grid configuration of a single semester within one academic year.

    Attributes:
        year_id: Owning academic year.
        period: Season key — ``"fall"`` or ``"spring"``.
        start_date: ISO date of the first study day, ``"yyyy-mm-dd"``.
        active_days: Seven booleans, Monday-first, marking teaching days.
        acad_min: Length of one academic hour, in minutes.
        slots: Ordered bell grid.
        slots_per_day: Cached ``len(slots)``.
        weeks_count: Number of teaching weeks in the semester.
        holidays: Non-teaching grid cells as ``"week-day"`` (0-based day).
    """

    year_id: int
    period: str
    start_date: str
    active_days: list[bool]
    acad_min: int
    slots: list[Slot]
    slots_per_day: int
    weeks_count: int
    holidays: list[str] = field(default_factory=list)


# Factory-default grid: 4×2 ac.h + 1×1 ac.h, each carrying its trailing break.
_DEFAULT_SLOTS: list[tuple[str, int, int]] = [
    ("08:30", 2, 15),
    ("10:20", 2, 30),
    ("12:25", 2, 10),
    ("14:10", 2, 15),
    ("16:00", 1, 15),
]
_DEFAULT_ACTIVE_DAYS: list[bool] = [True, True, True, True, True, False, False]
DEFAULT_ACAD_MIN: int = 45
DEFAULT_WEEKS_COUNT: int = 16


def default_slots() -> list[Slot]:
    """Return a fresh copy of the factory-default bell grid."""
    return [Slot(start=s, hours=h, brk=b) for s, h, b in _DEFAULT_SLOTS]


def ru_to_iso(date: str) -> str:
    """Convert a ``dd.mm.yyyy`` date to ISO ``yyyy-mm-dd`` (passthrough if unmatched)."""
    parts = date.split(".")
    if len(parts) == 3 and all(parts):
        day, month, year = parts
        return f"{year}-{month}-{day}"
    return date


def default_settings(year_id: int, period: str, ru_start_date: str) -> SemesterSettings:
    """Build factory-default semester settings for ``(year_id, period)``.

    Args:
        year_id: Owning academic year.
        period: Season key (``"fall"`` / ``"spring"``).
        ru_start_date: First study day as ``dd.mm.yyyy`` (converted to ISO).
    """
    return SemesterSettings(
        year_id=year_id,
        period=period,
        start_date=ru_to_iso(ru_start_date),
        active_days=list(_DEFAULT_ACTIVE_DAYS),
        acad_min=DEFAULT_ACAD_MIN,
        slots=default_slots(),
        slots_per_day=len(_DEFAULT_SLOTS),
        weeks_count=DEFAULT_WEEKS_COUNT,
        holidays=[],
    )
