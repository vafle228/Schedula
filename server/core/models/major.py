"""Major (специальность) — a study programme that owns groups."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Major:
    """A study programme.

    Attributes:
        id: Auto-assigned integer primary key.
        code: Official code, e.g. ``"09.02.07"``.
        name: Full programme name.
    """

    id: int
    code: str
    name: str
