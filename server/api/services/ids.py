"""Prefixed identifier allocation for new entities.

New ids are unique but need not reproduce the mock's exact values; they only
share the ``prefix + number`` / timestamp shapes so nothing downstream cares.

The allocators depend on the abstract repository ports rather than a concrete
unit of work, so services can hand in whichever port owns the id space.
"""

from __future__ import annotations

import re
import time
from collections.abc import Iterable

from core.repositories.discipline_repository import DisciplineRepository
from core.repositories.lesson_repository import LessonRepository
from core.repositories.teacher_repository import TeacherRepository

_TRAILING_NUMBER = re.compile(r"(\d+)$")


def _max_suffix(ids: Iterable[str]) -> int:
    """Return the largest trailing-number suffix across ``ids`` (0 if none)."""
    highest = 0
    for identifier in ids:
        match = _TRAILING_NUMBER.search(identifier)
        if match:
            highest = max(highest, int(match.group(1)))
    return highest


def _next(prefix: str, ids: Iterable[str]) -> str:
    return f"{prefix}{_max_suffix(ids) + 1}"


def timestamp_id(prefix: str) -> str:
    """Return ``prefix`` followed by the current epoch in milliseconds."""
    return f"{prefix}{int(time.time() * 1000)}"


def next_discipline_id(disciplines: DisciplineRepository) -> str:
    """Allocate the next free ``d<n>`` discipline id."""
    return _next("d", (d.id for d in disciplines.list_all()))


def next_topic_id(disciplines: DisciplineRepository) -> str:
    """Allocate the next free ``tp<n>`` topic id."""
    return _next("tp", (t.id for d in disciplines.list_all() for t in d.topics))


def next_lesson_id(lessons: LessonRepository) -> str:
    """Allocate the next free ``l<n>`` lesson id."""
    return _next("l", (l.id for l in lessons.list_all()))


def next_absence_id(teachers: TeacherRepository) -> str:
    """Allocate the next free ``ab<n>`` absence id."""
    return _next("ab", (a.id for t in teachers.list_all() for a in t.absences))


def slugify_topic_type(label: str | None, existing_keys: Iterable[str]) -> str:
    """Derive a unique machine key from a topic-type label.

    Mirrors the client's slug rule: lowercase, strip non-alphanumerics, cap at
    six characters, then disambiguate with a numeric suffix.
    """
    base = re.sub(r"[^a-zа-я0-9]+", "", (label or "тип").lower())[:6] or "type"
    taken = set(existing_keys)
    key = base
    counter = 1
    while key in taken:
        counter += 1
        key = f"{base}{counter}"
    return key
