"""Academic year — a pair of semesters (autumn + spring)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class YearStatus(StrEnum):
    """Lifecycle of an academic year."""

    DRAFT = "draft"
    ACTIVE = "active"
    DONE = "done"


@dataclass(slots=True)
class AcademicYear:
    """One academic year; only a single year may be ``ACTIVE`` at a time.

    Attributes:
        id: Stable identifier, e.g. ``"y2627"``.
        name: Display label, e.g. ``"2026/27"``.
        aut_from: Autumn start date, ``"dd.mm.yyyy"``.
        aut_to: Autumn end date, ``"dd.mm.yyyy"``.
        spr_from: Spring start date, ``"dd.mm.yyyy"``.
        spr_to: Spring end date, ``"dd.mm.yyyy"``.
        status: Lifecycle state.
    """

    id: str
    name: str
    aut_from: str
    aut_to: str
    spr_from: str
    spr_to: str
    status: YearStatus = YearStatus.DRAFT
