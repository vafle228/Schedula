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
    """A discipline taught to one group in one semester.

    Attributes:
        id: Auto-assigned integer primary key.
        name: Display name, e.g. ``"Матанализ"``.
        group_id: Group the discipline is taught to.
        period: Season key (``fall`` / ``spring``).
        is_new: Whether the discipline was added this session (UI highlight).
        topics: Owned topics.
    """

    id: int
    name: str
    group_id: str
    period: str
    is_new: bool = False
    topics: list[Topic] = field(default_factory=list)
