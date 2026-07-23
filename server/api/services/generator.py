"""Draft schedule generator — a faithful port of the client's ``generator.js``.

Greedy: each pending pair takes the earliest free slot (week → day → slot),
skipping hard/unfit cells and remembering the first soft cell as a fallback.
Lectures are placed before practicals. Pinned and orphaned lessons are never
moved.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from typing import Any

from api.services.conflicts import EnrichedLesson, slot_status
from core.models.period import Period
from core.models.teacher import Teacher


def compute_generation(
    enriched: list[EnrichedLesson],
    teachers: list[Teacher],
    cfg: Period,
    mode: str,
    kind_hours: Callable[[str], int],
) -> dict[str, Any]:
    """Compute placements without mutating ``enriched``.

    Args:
        enriched: The period's lessons as flat views.
        teachers: Teachers with constraints, for conflict checks.
        cfg: The period configuration (grid, weeks, holidays).
        mode: ``"rebuild"`` unplaces everything except pinned/orphaned first;
            ``"fill"`` keeps placed lessons and only seats the pool.
        kind_hours: Kind → academic-hours resolver.

    Returns:
        ``{"placements", "newIds", "placedN", "unplacedN", "softN", "moved",
        "unplaced"}``.
    """
    lessons = [replace(l) for l in enriched]
    day_idxs = [i for i, on in enumerate(cfg.active_days) if on]
    weeks_n = cfg.weeks_count or 16
    slots_n = len(cfg.slots) if cfg.slots else cfg.slots_per_day

    moved = 0
    if mode == "rebuild":
        for lesson in lessons:
            if lesson.d is not None and not lesson.pin and not lesson.orphan:
                lesson.w = lesson.d = lesson.s = None
                moved += 1

    todo = [l for l in lessons if l.d is None]
    todo.sort(key=lambda l: 0 if l.kind == "lec" else 1)  # stable: lectures first

    new_ids: list[int] = []
    soft_used = 0
    for lesson in todo:
        soft_best: tuple[int, int, int] | None = None
        placed = False
        for w in range(1, weeks_n + 1):
            for d in day_idxs:
                for s in range(slots_n):
                    status = slot_status(lesson, w, d, s, None, lessons, teachers, cfg, kind_hours)
                    if status["kind"] in ("hard", "unfit"):
                        continue
                    if status["kind"] == "soft":
                        if soft_best is None:
                            soft_best = (w, d, s)
                        continue
                    lesson.w, lesson.d, lesson.s = w, d, s
                    new_ids.append(lesson.id)
                    placed = True
                    break
                if placed:
                    break
            if placed:
                break
        if not placed and soft_best is not None:
            lesson.w, lesson.d, lesson.s = soft_best
            new_ids.append(lesson.id)
            soft_used += 1

    unplaced = [l for l in lessons if l.d is None]
    return {
        "placements": [{"id": l.id, "w": l.w, "d": l.d, "s": l.s} for l in lessons],
        "newIds": new_ids,
        "placedN": len(new_ids),
        "unplacedN": len(unplaced),
        "softN": soft_used,
        "moved": moved,
        "unplaced": [{"id": l.id, "disc": l.disc, "g": l.g, "kind": l.kind} for l in unplaced],
    }
