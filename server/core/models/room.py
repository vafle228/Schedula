"""Room (аудитория) — a physical teaching space."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Room:
    """A teaching room.

    The identifier doubles as the display name (e.g. ``"214"``, ``"к.412"``).

    Attributes:
        id: Room number / identifier.
        type: Room kind, e.g. ``"Лекционная"`` or ``"Комп. класс"``.
    """

    id: str
    type: str
