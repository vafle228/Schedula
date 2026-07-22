"""Teacher aggregate: the teacher, scheduling constraints and absences."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class AbsenceType(StrEnum):
    """Reason a teacher is unavailable for a stretch of the semester."""

    VACATION = "vacation"
    SICK = "sick"
    TRIP = "trip"
    OTHER = "other"


@dataclass(slots=True)
class Absence:
    """A period during which the teacher is away.

    Attributes:
        id: Stable identifier, e.g. ``"a1"``.
        teacher_id: Owning teacher.
        type: Reason for the absence.
        label: Free-text human span, e.g. ``"01–14 сентября"``.
    """

    id: str
    teacher_id: str
    type: AbsenceType
    label: str = ""


@dataclass(slots=True)
class TeacherConstraints:
    """Scheduling constraints attached to a teacher.

    Slot keys are ``"day-slot"`` strings (0-based day, 0-based slot).

    Attributes:
        hard: Slots the teacher is unavailable in (never scheduled there).
        soft: Slots the teacher would rather avoid (the generator avoids them).
        method: Methodical day index (0 = Monday) kept free, or ``None``.
        max_per_day: Cap on pairs per day, or ``None`` for no cap.
            Serialized to the frontend as ``max``.
    """

    hard: list[str] = field(default_factory=list)
    soft: list[str] = field(default_factory=list)
    method: int | None = None
    max_per_day: int | None = None


@dataclass(slots=True)
class Teacher:
    """A teacher and their attached scheduling data.

    Attributes:
        id: Stable identifier, e.g. ``"t1"``.
        name: Display name, e.g. ``"Орлова И.К."``.
        photo: Data-URL of the avatar, or ``None``.
        constraints: Scheduling constraints, or ``None`` when unset. A teacher
            with ``None`` constraints counts as "no constraints" in readiness.
        absences: Owned absence periods.
    """

    id: str
    name: str
    photo: str | None = None
    constraints: TeacherConstraints | None = None
    absences: list[Absence] = field(default_factory=list)
