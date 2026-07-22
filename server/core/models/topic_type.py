"""Topic (lesson) type catalogue entry — the single source of truth shared by
the plan and the schedule modules (``lec``, ``prac``, ``lab`` …).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class TopicType:
    """A lesson-type definition.

    Attributes:
        k: Stable machine key, e.g. ``"lec"``. Also the primary key.
        label: Full human label, e.g. ``"Лекция"``.
        short: Compact label for cards, e.g. ``"Лек."``.
        color: Base colour as ``"#RRGGBB"``; UI tints are derived from it.
        ac_hours: Academic hours a lesson of this type occupies (drives the
            slot-fit rule in conflict analysis).
    """

    k: str
    label: str
    short: str
    color: str
    ac_hours: int = 2
