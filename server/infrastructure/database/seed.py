"""Seed dataset — a faithful port of the client mock's ``seed.js``.

Builds the one coherent demo dataset (master data + plan + lesson slots) as
domain objects and persists it through the repositories, so a fresh database
matches what the frontend used to get from its in-memory mock.
"""

from __future__ import annotations

from core.models.academic_year import AcademicYear, YearStatus
from core.models.assignment import Assignment
from core.models.discipline import Discipline, Topic
from core.models.group import Group
from core.models.lesson import Lesson
from core.models.major import Major
from core.models.room import Room
from core.models.settings import default_settings
from core.models.teacher import Absence, AbsenceType, Teacher, TeacherConstraints
from core.models.topic_type import TopicType
from infrastructure.database.unit_of_work import SqliteUnitOfWork

# Factory-default topic types (also the client's DEFAULT_TOPIC_TYPES).
DEFAULT_TOPIC_TYPES: list[TopicType] = [
    TopicType("lec", "Лекция", "Лек.", "#3B62C4", 2),
    TopicType("grp", "Групповое занятие", "Гр.зан.", "#2563A8", 2),
    TopicType("prac", "Практика", "Практ.", "#1F8A5B", 2),
    TopicType("lab", "Лабораторная", "Лаб.", "#B45309", 2),
    TopicType("grpex", "Групповое упражнение", "Гр.упр.", "#0E9488", 2),
    TopicType("sem", "Семинар", "Сем.", "#8A3FFC", 2),
    TopicType("control", "Контрольная работа", "Контр.", "#9A3412", 2),
    TopicType("srs", "Руководство СРС", "СРС", "#6B7280", 2),
    TopicType("train", "Тренировка", "Трен.", "#0369A1", 2),
    TopicType("consult", "Консультация", "Конс.", "#0E7490", 1),
    TopicType("credit", "Зачёт", "Зач.", "#A16207", 2),
    TopicType("exam", "Экзамен", "Экз.", "#C0392B", 2),
    TopicType("course", "Курсовая", "Курс.", "#7A756C", 2),
]

# Demo holidays for the active year's grid, per season ("week-day", 0-based day).
_DEMO_HOLIDAYS: dict[str, list[str]] = {
    "fall": ["3-2", "11-0"],
    "spring": ["2-4", "10-0"],
}


def _seed_settings(
    uow: SqliteUnitOfWork, year: AcademicYear, holidays: dict[str, list[str]]
) -> None:
    """Create both semester settings for ``year`` from the factory defaults."""
    starts = {"fall": year.aut_from, "spring": year.spr_from}
    for period in ("fall", "spring"):
        settings = default_settings(year.id, period, starts[period])
        settings.holidays = list(holidays.get(period, []))
        uow.settings.save(settings)


def _constraints(
    hard: list[str], soft: list[str], method: int | None, max_per_day: int | None
) -> TeacherConstraints:
    return TeacherConstraints(hard=hard, soft=soft, method=method, max_per_day=max_per_day)


# (key, name, constraints | None, [(type, label), ...])
_TEACHERS: list[tuple[str, str, TeacherConstraints | None, list[tuple[str, str]]]] = [
    ("t1", "Орлова И.К.", _constraints(["0-6", "1-6"], [], 2, 4),
     [("vacation", "01–14 сентября"), ("trip", "20–22 октября")]),
    ("t2", "Ким Д.С.", _constraints(["0-0", "0-1"], ["4-5", "4-6"], None, 3), []),
    ("t3", "Стеклов П.А.", _constraints([], ["0-0"], 4, 4),
     [("vacation", "10–24 марта")]),
    ("t4", "Белов А.Н.", None, []),
    ("t5", "Юсупова Р.М.", _constraints(["3-5", "3-6", "4-5", "4-6"], [], None, None),
     [("vacation", "07–20 октября"), ("sick", "03–05 ноября")]),
    ("t6", "Дроздова Е.В.", _constraints([], ["0-5", "0-6"], None, 4), []),
    ("t7", "Гарин О.Л.", None, []),
    ("t8", "Мельник С.С.", _constraints(["2-0", "2-1", "2-2"], [], None, 4),
     [("vacation", "01–14 апреля")]),
    ("t9", "Ахматова Л.Р.", None, []),
    ("t10", "Козлов В.П.", None, []),
]

_ROOMS: list[tuple[str, str, int]] = [
    ("214", "Лекционная", 80), ("118", "Лекционная", 120),
    ("301", "Лекционная", 60), ("305", "Лекционная", 40),
    ("220", "Лекционная", 50), ("к.412", "Комп. класс", 25),
    ("к.413", "Комп. класс", 25), ("лаб.2", "Лаборатория", 20),
]

# (key, code, name)
_MAJORS: list[tuple[str, str, str]] = [
    ("m1", "09.02.07", "Информационные системы и программирование"),
    ("m2", "09.02.03", "Программирование в компьютерных системах"),
    ("m3", "38.02.01", "Экономика и бухгалтерский учёт"),
    ("m4", "40.02.04", "Юриспруденция"),
]

# (group_name, major_key, course)
_GROUPS: list[tuple[str, str, int]] = [
    ("ИС-31", "m1", 3), ("ИС-32", "m1", 3), ("ИС-21", "m1", 2), ("ИС-11", "m1", 1),
    ("ПКС-21", "m2", 2), ("ПКС-22", "m2", 2), ("ЭК-11", "m3", 1),
]

# (group, discipline, kind, teacher_key|None, room, placed[(day,slot)...], extra, opts)
_SPEC: list[tuple] = [
    ("ИС-31", "Матанализ", "lec", "t1", "214", [(0, 0)], 0, {}),
    ("ИС-31", "Матанализ", "prac", "t1", "214", [(0, 1)], 1, {}),
    ("ИС-31", "Программирование", "prac", "t2", "к.412", [(1, 0)], 1, {}),
    ("ИС-31", "Программирование", "lec", "t2", "214", [(4, 3)], 0, {}),
    ("ИС-31", "Физика", "lec", "t3", "118", [(3, 0)], 0, {}),
    ("ИС-31", "История", "lec", "t4", "301", [(1, 1)], 0, {}),
    ("ИС-31", "БЖД", "lec", "t5", "220", [(2, 1)], 0, {}),
    ("ИС-31", "Англ. язык", "prac", "t6", "305", [(4, 1)], 1, {}),
    ("ИС-31", "Базы данных", "prac", "t2", "к.413", [], 2, {}),
    ("ИС-32", "История", "lec", "t4", "301", [(1, 1)], 0, {}),
    ("ИС-32", "Матанализ", "lec", "t1", "214", [(1, 0)], 1, {}),
    ("ИС-32", "Философия", "lec", None, "305", [(3, 2)], 0, {"orphanTeacher": "t9"}),
    ("ИС-32", "Программирование", "prac", "t2", "к.412", [(2, 3)], 1, {}),
    ("ИС-32", "Физика", "lec", "t3", "118", [(3, 1)], 0, {}),
    ("ИС-32", "Англ. язык", "prac", "t6", "305", [(0, 2)], 1, {}),
    ("ПКС-21", "Веб-разработка", "prac", "t7", "к.413", [(0, 0), (2, 0)], 1, {}),
    ("ПКС-21", "ОС и сети", "lec", "t8", "220", [(1, 2)], 1, {}),
    ("ПКС-21", "Матанализ", "lec", "t1", "118", [(3, 2)], 0, {}),
    ("ПКС-21", "История", "lec", "t4", "301", [(4, 0)], 0, {}),
    ("ПКС-21", "Базы данных", "prac", "t10", "к.412", [], 2, {}),
    ("ПКС-22", "Веб-разработка", "prac", "t7", "к.413", [(0, 1), (2, 1)], 0, {}),
    ("ПКС-22", "ОС и сети", "lec", "t8", "220", [(4, 2)], 1, {}),
    ("ПКС-22", "Англ. язык", "prac", "t6", "305", [(1, 3)], 1, {}),
    ("ПКС-22", "Физика", "lec", "t3", "118", [(2, 3)], 0, {}),
    ("ПКС-22", "История", "lec", "t4", "301", [], 1, {}),
    ("ЭК-11", "Статистика", "lec", "t8", "214", [(0, 0)], 0, {}),
    ("ЭК-11", "Экономика", "lec", "t9", "301", [(0, 3), (2, 2)], 1, {}),
    ("ЭК-11", "Матанализ", "prac", "t1", "305", [(1, 2)], 1, {}),
    ("ЭК-11", "Англ. язык", "prac", "t6", "305", [(3, 3)], 0, {}),
    ("ЭК-11", "Информатика", "prac", "t10", "к.412", [], 2, {}),
]

_THEMES: dict[str, tuple[str, str]] = {
    "ИС-31|Матанализ|lec": ("Тема 4. Пределы и непрерывность",
                            "Предел функции в точке. Односторонние пределы"),
    "ИС-31|Матанализ|prac": ("Тема 4. Пределы и непрерывность",
                             "Вычисление пределов: раскрытие неопределённостей"),
    "ИС-31|Программирование|prac": ("Тема 2. Структуры данных",
                                    "Списки, словари, множества: типовые операции"),
    "ИС-31|Программирование|lec": ("Тема 2. Структуры данных",
                                   "Абстрактные типы данных. Сложность операций"),
    "ИС-31|Физика|lec": ("Тема 3. Динамика материальной точки",
                         "Законы Ньютона. Силы в механике"),
    "ИС-31|БЖД|lec": ("Тема 1. Основы безопасности",
                      "Классификация опасных и вредных факторов"),
    "ИС-32|Матанализ|lec": ("Тема 4. Пределы и непрерывность",
                            "Предел функции в точке. Односторонние пределы"),
    "ПКС-21|Веб-разработка|prac": ("Тема 5. Клиент-серверное взаимодействие",
                                   "REST API: методы, коды ответов, форматы"),
    "ПКС-21|ОС и сети|lec": ("Тема 3. Процессы и потоки",
                             "Планирование процессов. Состояния потока"),
    "ЭК-11|Экономика|lec": ("Тема 1. Спрос и предложение",
                            "Рыночное равновесие. Эластичность спроса"),
    "ЭК-11|Статистика|lec": ("Тема 2. Ряды распределения",
                             "Средние величины и показатели вариации"),
}

# group, name, period, [(kind, topic_name, hours), ...]
_EXTRA_PLAN: list[tuple[str, str, str, list[tuple[str, str, int]]]] = [
    ("ИС-21", "Психология общения", "fall", [("lec", "Теоретический курс", 32)]),
    ("ИС-11", "Русский язык", "fall", [("prac", "Практические занятия", 64)]),
    ("ИС-31", "Теория вероятностей", "spring",
     [("lec", "Теоретический курс", 32), ("prac", "Практикум", 32)]),
    ("ИС-32", "ООП", "spring",
     [("lec", "Лекционный раздел", 32), ("prac", "Лабораторный практикум", 64)]),
    ("ИС-21", "Дискретная математика", "spring",
     [("lec", "Раздел 1. Основы", 32), ("prac", "Семинары", 32)]),
    ("ПКС-21", "Мобильная разработка", "spring",
     [("prac", "Практикум", 64), ("lec", "Вводный раздел", 32)]),
    ("ПКС-22", "Тестирование ПО", "spring",
     [("lec", "Теория", 32), ("prac", "Практикум", 32)]),
    ("ЭК-11", "Маркетинг", "spring", [("lec", "Теоретический курс", 32)]),
]


def _topic_name(kind: str) -> str:
    return "Теоретический курс" if kind == "lec" else "Практические занятия"


def seed(uow: SqliteUnitOfWork) -> None:
    """Populate an (empty) database with the demo dataset.

    Args:
        uow: A unit of work whose schema has already been initialised.
    """
    active_year: AcademicYear | None = None
    for year_data in [
        ("2025/26", "01.09.2025", "28.12.2025", "09.02.2026", "31.05.2026", YearStatus.DONE),
        ("2026/27", "01.09.2026", "27.12.2026", "08.02.2027", "30.05.2027", YearStatus.ACTIVE),
        ("2027/28", "01.09.2027", "26.12.2027", "07.02.2028", "28.05.2028", YearStatus.DRAFT),
    ]:
        name, af, at, sf, st, status = year_data
        year = AcademicYear(id=0, name=name, aut_from=af, aut_to=at,
                            spr_from=sf, spr_to=st, status=status)
        uow.years.add(year)
        # Only the active year carries the demo grid holidays; others use defaults.
        is_active = status == YearStatus.ACTIVE
        _seed_settings(uow, year, _DEMO_HOLIDAYS if is_active else {})
        if is_active:
            active_year = year

    assert active_year is not None
    year_id = active_year.id

    for topic_type in DEFAULT_TOPIC_TYPES:
        uow.topic_types.add(topic_type)

    teacher_ids: dict[str, int] = {}
    for key, name, constraints, absences_data in _TEACHERS:
        t = Teacher(id=0, name=name, photo=None, constraints=constraints)
        uow.teachers.add(t)
        teacher_ids[key] = t.id
        for atype, label in absences_data:
            uow.absences.add(Absence(id=0, teacher_id=t.id, type=AbsenceType(atype), label=label))

    for room_id, room_type, capacity in _ROOMS:
        uow.rooms.add(Room(room_id, room_type, capacity))

    major_ids: dict[str, int] = {}
    for key, code, name in _MAJORS:
        m = Major(id=0, code=code, name=name)
        uow.majors.add(m)
        major_ids[key] = m.id

    group_ids: dict[str, int] = {}
    for gname, major_key, course in _GROUPS:
        group = Group(
            id=0, year_id=year_id, name=gname,
            major_id=major_ids[major_key], course=course,
        )
        uow.groups.add(group)
        group_ids[gname] = group.id

    # A group's (major, course) — the scope a discipline is now shared across.
    group_meta: dict[str, tuple[int, int]] = {
        gname: (major_ids[mkey], course) for gname, mkey, course in _GROUPS
    }
    # (major_id, course, period, name) -> shared Discipline
    disc_by_key: dict[tuple[int, int, str, str], Discipline] = {}
    # (discipline_id, kind) -> Topic shared by every group of that major/course
    topic_by_key: dict[tuple[int, str], Topic] = {}

    def _discipline(major_id: int, course: int, period: str, name: str) -> Discipline:
        key = (major_id, course, period, name)
        discipline = disc_by_key.get(key)
        if discipline is None:
            discipline = Discipline(
                id=0, year_id=year_id, name=name, major_id=major_id,
                course=course, period=period, is_new=False, topics=[],
            )
            uow.disciplines.add(discipline)
            disc_by_key[key] = discipline
        return discipline

    def _topic(discipline: Discipline, kind: str, name: str, hours: int) -> Topic:
        key = (discipline.id, kind)
        topic = topic_by_key.get(key)
        if topic is None:
            topic = Topic(
                id=0, discipline_id=discipline.id, kind=kind, name=name, hours=hours,
            )
            uow.topics.add(topic)
            topic_by_key[key] = topic
        return topic

    for group, disc, kind, teacher_key, room_id, placed, extra, opts in _SPEC:
        major_id, course = group_meta[group]
        discipline = _discipline(major_id, course, "fall", disc)
        pairs = len(placed) + extra
        topic = _topic(discipline, kind, _topic_name(kind), pairs * 32)
        group_id = group_ids[group]

        teacher_id: int | None = teacher_ids.get(teacher_key) if teacher_key else None
        if teacher_id is not None:
            uow.assignments.set(
                Assignment(group_id, topic.id, teacher_id, pairs_per_week=pairs)
            )

        theme = _THEMES.get(f"{group}|{disc}|{kind}")
        label = theme[0] if theme else ""
        question = theme[1] if theme else ""
        orphan_key: str | None = opts.get("orphanTeacher")
        owner: int | None = teacher_id or (teacher_ids.get(orphan_key) if orphan_key else None)

        for i, (day, slot) in enumerate(placed):
            uow.lessons.add(Lesson(
                id=0, year_id=year_id, topic_id=topic.id, discipline_id=discipline.id,
                group_id=group_id, teacher_id=owner, room_id=room_id, kind=kind,
                period="fall", week=1, day=day, slot=slot, sub_by=None,
                manual=False, ni=i + 1, nt=pairs,
                topic_label=label, question=question,
            ))

        if teacher_id is not None:
            for i in range(extra):
                uow.lessons.add(Lesson(
                    id=0, year_id=year_id, topic_id=topic.id, discipline_id=discipline.id,
                    group_id=group_id, teacher_id=teacher_id, room_id=room_id,
                    kind=kind, period="fall", week=None, day=None, slot=None, sub_by=None,
                    manual=False, ni=len(placed) + i + 1, nt=pairs,
                    topic_label=label, question=question,
                ))

    for group, name, period, topics in _EXTRA_PLAN:
        major_id, course = group_meta[group]
        discipline = _discipline(major_id, course, period, name)
        for kind, topic_name, hours in topics:
            _topic(discipline, kind, topic_name, hours)

    uow.commit()
