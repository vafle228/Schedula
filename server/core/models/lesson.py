"""Lesson slot — one concrete pair, placed on the grid or waiting in the pool.

A lesson may be *placed* (``week``/``day``/``slot`` all set) or *pooled*
(all three ``None``). It is *auto* (``manual`` false) when it was materialised
from an assigned topic by the sync rules, or *manual* when created by hand in
the schedule module.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Lesson:
    """A single lesson occurrence.

    Attributes:
        id: Stable identifier, e.g. ``"l1"``.
        topic_id: Source topic, or ``None`` for a free manual lesson.
        discipline_id: Owning discipline, or ``None``.
        group_id: Group the lesson is for.
        teacher_id: Assigned (staff) teacher, or ``None``.
        room_id: Room, or ``None``.
        kind: Topic-type key (``lec`` / ``prac`` / …).
        period: Season key (``fall`` / ``spring``).
        week: 1-based teaching week, or ``None`` when pooled.
        day: 0-based day index (0 = Monday), or ``None``.
        slot: 0-based slot index, or ``None``.
        sub_by: Substitute teacher id for this occurrence, or ``None``.
        pin: Whether the placement is pinned against regeneration.
        manual: ``True`` for hand-made lessons, ``False`` for auto ones.
        ni: 1-based ordinal of this pair within its topic.
        nt: Total pairs of the topic.
        topic_label: Display theme label, e.g. ``"Тема 4. …"``.
        question: Study question / subtopic text.
    """

    id: str
    group_id: str
    kind: str
    period: str
    topic_id: str | None = None
    discipline_id: str | None = None
    teacher_id: str | None = None
    room_id: str | None = None
    week: int | None = None
    day: int | None = None
    slot: int | None = None
    sub_by: str | None = None
    pin: bool = False
    manual: bool = True
    ni: int = 1
    nt: int = 1
    topic_label: str = ""
    question: str = ""
