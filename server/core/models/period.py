"""Semester (period) configuration — the schedule grid definition.

A period owns the bell grid (`slots`), the active week days, holiday cells and
the number of teaching weeks. Two periods live per academic year: ``fall`` and
``spring`` (their ids double as the season key).
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
class Period:
    """Configuration of a single semester.

    Attributes:
        id: Season key — ``"fall"`` or ``"spring"``.
        date_from: Human date the semester starts, ``"dd.mm.yyyy"``.
        date_to: Human date the semester ends, ``"dd.mm.yyyy"``.
        start_date: ISO date of the first study day, ``"yyyy-mm-dd"``.
        active_days: Seven booleans, Monday-first, marking teaching days.
        acad_min: Length of one academic hour, in minutes.
        slots: Ordered bell grid.
        slots_per_day: Cached ``len(slots)``.
        weeks_count: Number of teaching weeks in the semester.
        holidays: Non-teaching grid cells as ``"week-day"`` (0-based day).
    """

    id: str
    date_from: str
    date_to: str
    start_date: str
    active_days: list[bool]
    acad_min: int
    slots: list[Slot]
    slots_per_day: int
    weeks_count: int
    holidays: list[str] = field(default_factory=list)
