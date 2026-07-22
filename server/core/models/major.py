"""Major (специальность) — a study programme that owns groups."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Major:
    """A study programme.

    Attributes:
        id: Stable identifier, e.g. ``"m1"``.
        code: Official code, e.g. ``"09.02.07"``.
        name: Full programme name.
    """

    id: str
    code: str
    name: str
