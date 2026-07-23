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
from core.models.period import Period
from core.models.room import Room
from core.models.teacher import Absence, Teacher, TeacherConstraints
from core.models.topic_type import TopicType


def period(p: Period) -> dict[str, Any]:
    return {
        "id": p.id,
        "dateFrom": p.date_from,
        "dateTo": p.date_to,
        "startDate": p.start_date,
        "activeDays": p.active_days,
        "acadMin": p.acad_min,
        "slots": [asdict(s) for s in p.slots],
        "slotsPerDay": p.slots_per_day,
        "weeksCount": p.weeks_count,
        "holidays": p.holidays,
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
    return {"id": g.id, "majorId": g.major_id, "course": g.course}


def topic(t: Topic) -> dict[str, Any]:
    return {"id": t.id, "kind": t.kind, "name": t.name, "hours": t.hours}


def discipline(d: Discipline) -> dict[str, Any]:
    return {
        "id": d.id,
        "name": d.name,
        "groupId": d.group_id,
        "period": d.period,
        "isNew": d.is_new,
        "topics": [topic(t) for t in d.topics],
    }


def assignment(a: Assignment) -> dict[str, Any]:
    return {"teacherId": a.teacher_id, "pairsPerWeek": a.pairs_per_week}


def assignments_map(items: dict[str, Assignment]) -> dict[str, Any]:
    return {topic_id: assignment(a) for topic_id, a in items.items()}


def lesson(l: Lesson) -> dict[str, Any]:
    return {
        "id": l.id,
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
        "pin": l.pin,
        "manual": l.manual,
        "ni": l.ni,
        "nt": l.nt,
        "topicLabel": l.topic_label,
        "question": l.question,
    }
