"""Discipline and its topics — the plan side (Распределение)."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class Topic:
    """A topic (раздел) of a discipline; the unit that gets a teacher assigned.

    Attributes:
        id: Auto-assigned integer primary key.
        discipline_id: Owning discipline.
        kind: Topic-type key (``lec`` / ``prac`` / …).
        name: Display name, e.g. ``"Теоретический курс"``.
        hours: Total academic hours planned for the topic.
    """

    id: int
    discipline_id: int
    kind: str
    name: str
    hours: int


@dataclass(slots=True)
class Discipline:
    """A discipline in one major's course-year and semester of an academic year.

    A discipline belongs to a *(major, course)* — not to a group — so its plan
    (topics and hours) is shared by every group of that major and course. Which
    teacher delivers each topic is decided per group (see :class:`Assignment`).
    The same subject taught to several majors with different hours is simply
    several discipline rows that happen to share a ``name``.

    Attributes:
        id: Auto-assigned integer primary key.
        year_id: Owning academic year.
        name: Display name, e.g. ``"Матанализ"``.
        major_id: Major the discipline belongs to.
        course: Course-year within the major (1..4) the discipline is taught in.
        period: Season key (``fall`` / ``spring``).
        is_new: Whether the discipline was added this session (UI highlight).
        topics: Owned topics.
    """

    id: int
    year_id: int
    name: str
    major_id: int
    course: int
    period: str
    is_new: bool = False
    topics: list[Topic] = field(default_factory=list)
