"""Student group — belongs to a major, sits at a course (year of study)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Group:
    """A study group.

    The identifier doubles as the display name (e.g. ``"ИС-31"``), matching the
    frontend data schema.

    Attributes:
        id: Group name / identifier, e.g. ``"ИС-31"``.
        major_id: Owning major.
        course: Year of study (1-based).
    """

    id: str
    major_id: int
    course: int
