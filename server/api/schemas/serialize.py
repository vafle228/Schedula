"""Serialization: domain objects → frontend JSON dicts (camelCase shapes).

The frontend contract is the source of truth; these functions produce exactly
the payloads the client (and its former mock) expect.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from core.models.academic_year import AcademicYear
from core.models.assignment import Assignment
from core.models.discipline import Discipline, Topic
from core.models.group import Group
from core.models.lesson import Lesson
from core.models.major import Major
from core.models.room import Room
from core.models.settings import SemesterSettings
from core.models.teacher import Absence, Teacher, TeacherConstraints
from core.models.topic_type import TopicType


def settings(s: SemesterSettings, y: AcademicYear) -> dict[str, Any]:
    """Serialize one semester's settings; calendar dates come from the year.

    ``id`` is the season key so the client keeps its ``{id: 'fall', …}`` shape.
    """
    fall = s.period == "fall"
    return {
        "id": s.period,
        "yearId": s.year_id,
        "period": s.period,
        "dateFrom": y.aut_from if fall else y.spr_from,
        "dateTo": y.aut_to if fall else y.spr_to,
        "startDate": s.start_date,
        "activeDays": s.active_days,
        "acadMin": s.acad_min,
        "slots": [asdict(slot) for slot in s.slots],
        "slotsPerDay": s.slots_per_day,
        "weeksCount": s.weeks_count,
        "holidays": s.holidays,
    }


def year(y: AcademicYear) -> dict[str, Any]:
    return {
        "id": y.id,
        "name": y.name,
        "autFrom": y.aut_from,
        "autTo": y.aut_to,
        "sprFrom": y.spr_from,
        "sprTo": y.spr_to,
        "status": str(y.status),
    }


def topic_type(t: TopicType, used: int | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "k": t.k,
        "label": t.label,
        "short": t.short,
        "color": t.color,
        "acHours": t.ac_hours,
    }
    if used is not None:
        data["used"] = used
    return data


def constraints(c: TeacherConstraints | None) -> dict[str, Any] | None:
    if c is None:
        return None
    return {"hard": c.hard, "soft": c.soft, "method": c.method, "max": c.max_per_day}


def absence(a: Absence) -> dict[str, Any]:
    return {"id": a.id, "type": str(a.type), "label": a.label}


def teacher(t: Teacher) -> dict[str, Any]:
    return {
        "id": t.id,
        "name": t.name,
        "photo": t.photo,
        "c": constraints(t.constraints),
        "absences": [absence(a) for a in t.absences],
    }


def room(r: Room, used: int | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {"id": r.id, "type": r.type, "capacity": r.capacity}
    if used is not None:
        data["used"] = used
    return data


def major(m: Major, groups_count: int | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {"id": m.id, "code": m.code, "name": m.name}
    if groups_count is not None:
        data["groupsCount"] = groups_count
    return data


def group(g: Group) -> dict[str, Any]:
    return {"id": g.id, "name": g.name, "majorId": g.major_id, "course": g.course}


def topic(t: Topic) -> dict[str, Any]:
    return {"id": t.id, "kind": t.kind, "name": t.name, "hours": t.hours}


def discipline(d: Discipline) -> dict[str, Any]:
    return {
        "id": d.id,
        "yearId": d.year_id,
        "name": d.name,
        "majorId": d.major_id,
        "course": d.course,
        "period": d.period,
        "isNew": d.is_new,
        "topics": [topic(t) for t in d.topics],
    }


def assignment(a: Assignment) -> dict[str, Any]:
    return {"teacherId": a.teacher_id, "pairsPerWeek": a.pairs_per_week}


def assignments_map(items: dict[tuple[int, int], Assignment]) -> dict[str, Any]:
    """Serialize assignments as a nested ``{groupId: {topicId: assignment}}`` map."""
    out: dict[str, dict[str, Any]] = {}
    for (group_id, topic_id), a in items.items():
        out.setdefault(str(group_id), {})[str(topic_id)] = assignment(a)
    return out


def lesson(l: Lesson) -> dict[str, Any]:
    return {
        "id": l.id,
        "yearId": l.year_id,
        "topicId": l.topic_id,
        "disciplineId": l.discipline_id,
        "groupId": l.group_id,
        "teacherId": l.teacher_id,
        "roomId": l.room_id,
        "kind": l.kind,
        "period": l.period,
        "week": l.week,
        "day": l.day,
        "slot": l.slot,
        "subBy": l.sub_by,
        "manual": l.manual,
        "ni": l.ni,
        "nt": l.nt,
        "topicLabel": l.topic_label,
        "question": l.question,
        "number": l.number,
    }
