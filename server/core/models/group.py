"""Student group — belongs to a major, sits at a course (year of study)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Group:
    """A study group, scoped to one academic year.

    Groups carry an integer surrogate id; the display ``name`` (e.g. ``"ИС-31"``)
    is a plain field. Each year owns its own group rows, so the same name may
    recur across years with distinct ids — all references go by id.

    Attributes:
        id: Auto-assigned integer primary key.
        year_id: Owning academic year.
        name: Display name, e.g. ``"ИС-31"``.
        major_id: Owning major.
        course: Year of study (1-based).
    """

    id: int
    year_id: int
    name: str
    major_id: int
    course: int
    leader_id: int | None = None
