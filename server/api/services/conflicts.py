"""Conflict analysis — a faithful port of the client's ``conflicts.js``.

Operates on lightweight :class:`EnrichedLesson` views (week/day/slot are 1-based
week, 0-based day, 0-based slot, or ``None`` when the lesson sits in the pool).
Conflicts are always computed, never stored.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from core.models.period import Period
from core.models.teacher import Teacher


@dataclass(slots=True)
class EnrichedLesson:
    """Flat lesson view used by the conflict engine and the generator."""

    id: str
    g: str  # group id
    disc: str  # discipline name
    t: str | None  # staff teacher id
    room: str | None
    kind: str
    w: int | None  # week (1-based)
    d: int | None  # day (0 = Monday)
    s: int | None  # slot index
    sub_by: str | None  # substitute teacher id
    pin: bool
    orphan: bool


def eff_teacher(lesson: EnrichedLesson) -> str | None:
    """Effective teacher of an occurrence — the substitute if one is set."""
    return lesson.sub_by or lesson.t


def slot_fits(kind: str, s: int, cfg: Period, kind_hours: Callable[[str], int]) -> bool:
    """True when a lesson of ``kind`` fits slot ``s`` of the given config."""
    if not cfg or not cfg.slots or s >= len(cfg.slots):
        return True
    return kind_hours(kind) <= cfg.slots[s].hours


def is_holiday(cfg: Period, w: int | None, d: int | None) -> bool:
    """True when the ``(week, day)`` cell is a holiday in ``cfg``."""
    return bool(cfg and cfg.holidays and f"{w}-{d}" in cfg.holidays)


def analyze(
    lessons: list[EnrichedLesson],
    teachers: list[Teacher],
    cfg: Period | None,
    kind_hours: Callable[[str], int],
) -> dict[str, Any]:
    """Full conflict pass over placed lessons.

    Returns:
        ``{"byId": {lessonId: [{"sev", "text"}]}, "hardN", "softN", "orphanN"}``
        where ``sev`` is ``"hard" | "soft" | "orphan"``.
    """
    by_id: dict[str, list[dict[str, str]]] = {}

    def add(lesson_id: str, sev: str, text: str) -> None:
        by_id.setdefault(lesson_id, []).append({"sev": sev, "text": text})

    tmap = {t.id: t for t in teachers}

    for lesson in lessons:
        if lesson.orphan and lesson.d is not None:
            add(lesson.id, "orphan", "Назначение снято в «Распределении» — пара осиротела")

    placed = [l for l in lessons if l.d is not None and not l.orphan]

    def group_by(key: Callable[[EnrichedLesson], str]) -> dict[str, list[EnrichedLesson]]:
        buckets: dict[str, list[EnrichedLesson]] = {}
        for lesson in placed:
            buckets.setdefault(key(lesson), []).append(lesson)
        return buckets

    for bucket in group_by(lambda l: f"{eff_teacher(l)}|{l.w}|{l.d}|{l.s}").values():
        if len(bucket) > 1:
            for lesson in bucket:
                add(lesson.id, "hard", "Преподаватель в двух местах одновременно")
    for bucket in group_by(lambda l: f"{l.g}|{l.w}|{l.d}|{l.s}").values():
        if len(bucket) > 1:
            for lesson in bucket:
                add(lesson.id, "hard", "Группа в двух местах одновременно")
    for bucket in group_by(lambda l: f"{l.room}|{l.w}|{l.d}|{l.s}").values():
        if len(bucket) > 1:
            for lesson in bucket:
                add(lesson.id, "hard", f"Аудитория {lesson.room} занята")

    if cfg:
        slots_n = len(cfg.slots) if cfg.slots else cfg.slots_per_day
        for lesson in placed:
            if (cfg.active_days and cfg.active_days[lesson.d] is False) or (
                slots_n and lesson.s >= slots_n
            ):
                add(lesson.id, "hard",
                    "Пара вне учебной недели или сетки звонков (см. «Настройки»)")
            elif is_holiday(cfg, lesson.w, lesson.d):
                add(lesson.id, "hard", "Пара выпадает на праздничный день")
            elif not slot_fits(lesson.kind, lesson.s, cfg, kind_hours):
                add(lesson.id, "hard", "Занятие 2 ак.ч в слоте на 1 ак.ч (см. «Настройки»)")

    for lesson in placed:
        teacher = tmap.get(eff_teacher(lesson))
        c = teacher.constraints if teacher else None
        if not c:
            continue
        key = f"{lesson.d}-{lesson.s}"
        if c.method == lesson.d:
            add(lesson.id, "hard", "Методический день преподавателя")
        elif key in c.hard:
            add(lesson.id, "hard", "Преподаватель недоступен в этот слот")
        elif key in c.soft:
            add(lesson.id, "soft", "Нежелательный слот преподавателя")

    for bucket in group_by(lambda l: f"{eff_teacher(l)}|{l.w}|{l.d}").values():
        teacher = tmap.get(eff_teacher(bucket[0]))
        c = teacher.constraints if teacher else None
        if c and c.max_per_day and len(bucket) > c.max_per_day:
            for lesson in bucket:
                add(lesson.id, "hard", f"Превышен максимум пар в день ({c.max_per_day})")

    hard_n = soft_n = orphan_n = 0
    for issues in by_id.values():
        sevs = [x["sev"] for x in issues]
        if "hard" in sevs:
            hard_n += 1
        elif "orphan" in sevs:
            orphan_n += 1
        else:
            soft_n += 1
    return {"byId": by_id, "hardN": hard_n, "softN": soft_n, "orphanN": orphan_n}


def slot_status(
    lesson: EnrichedLesson,
    w: int,
    d: int,
    s: int,
    room: str | None,
    lessons: list[EnrichedLesson],
    teachers: list[Teacher],
    cfg: Period,
    kind_hours: Callable[[str], int],
) -> dict[str, str]:
    """Status of dropping ``lesson`` into ``(w, d, s)`` with room ``room``.

    Returns ``{"kind": "free"|"soft"|"hard"|"unfit", "text": ...}``.
    """
    tmap = {t.id: t for t in teachers}
    eff = eff_teacher(lesson)
    teacher = tmap.get(eff)
    tname = teacher.name if teacher else ""

    if not slot_fits(lesson.kind, s, cfg, kind_hours):
        return {"kind": "unfit", "text": "Занятие 2 ак.ч не помещается в слот на 1 ак.ч"}
    if is_holiday(cfg, w, d):
        return {"kind": "unfit", "text": "Праздничный день — занятия не ставятся"}

    others = [
        x for x in lessons
        if x.id != lesson.id and x.w == w and x.d == d and x.s == s and not x.orphan
    ]
    if any(eff_teacher(x) == eff for x in others):
        return {"kind": "hard", "text": f"Преподаватель {tname} уже занят в этом слоте"}
    if any(x.g == lesson.g for x in others):
        return {"kind": "hard", "text": f"Группа {lesson.g} уже занята в этом слоте"}
    target_room = room or lesson.room
    if any(x.room == target_room for x in others):
        return {"kind": "hard", "text": f"Аудитория {target_room} занята"}

    c = teacher.constraints if teacher else None
    if c:
        key = f"{d}-{s}"
        if c.method == d:
            return {"kind": "hard", "text": "Методический день преподавателя"}
        if key in c.hard:
            return {"kind": "hard", "text": "Преподаватель недоступен в этот слот"}
        if c.max_per_day:
            same_day = [
                x for x in lessons
                if x.id != lesson.id and eff_teacher(x) == eff
                and x.w == w and x.d == d and not x.orphan
            ]
            if len(same_day) + 1 > c.max_per_day:
                return {"kind": "hard",
                        "text": f"Превышен максимум пар в день ({c.max_per_day})"}
        if key in c.soft:
            return {"kind": "soft",
                    "text": "Нежелательный слот преподавателя — можно, но генератор бы избегал"}

    return {"kind": "free", "text": "Слот свободен, конфликтов нет"}
