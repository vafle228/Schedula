"""Database schema (DDL) and initialisation.

Auto-generated identifiers use ``INTEGER PRIMARY KEY`` (SQLite rowid alias,
effectively AUTOINCREMENT). Semantic/natural keys that double as display names
— ``periods.id`` (``fall``/``spring``), ``rooms.id``, ``groups.id``,
``topic_types.k`` — stay ``TEXT``.

Structured sub-objects that have no query needs — period
``slots``/``active_days``/``holidays`` and teacher ``constraints`` — are stored
as JSON ``TEXT`` and hydrated by the repositories.

Insertion order (which several list endpoints preserve) is read back via each
table's implicit ``rowid``; no explicit ordering column is needed.
"""

from __future__ import annotations

import sqlite3

SCHEMA: str = """
CREATE TABLE IF NOT EXISTS periods (
    id            TEXT PRIMARY KEY,
    date_from     TEXT NOT NULL,
    date_to       TEXT NOT NULL,
    start_date    TEXT NOT NULL,
    active_days   TEXT NOT NULL,   -- JSON: [bool x7]
    acad_min      INTEGER NOT NULL,
    slots         TEXT NOT NULL,   -- JSON: [{start,hours,brk}]
    slots_per_day INTEGER NOT NULL,
    weeks_count   INTEGER NOT NULL,
    holidays      TEXT NOT NULL    -- JSON: ["w-d", ...]
);

CREATE TABLE IF NOT EXISTS academic_years (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    aut_from TEXT NOT NULL,
    aut_to   TEXT NOT NULL,
    spr_from TEXT NOT NULL,
    spr_to   TEXT NOT NULL,
    status   TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS topic_types (
    k        TEXT PRIMARY KEY,
    label    TEXT NOT NULL,
    short    TEXT NOT NULL,
    color    TEXT NOT NULL,
    ac_hours INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS teachers (
    id          INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    photo       TEXT,
    constraints TEXT               -- JSON: {hard,soft,method,max} or NULL
);

CREATE TABLE IF NOT EXISTS absences (
    id         INTEGER PRIMARY KEY,
    teacher_id INTEGER NOT NULL REFERENCES teachers(id) ON DELETE CASCADE,
    type       TEXT NOT NULL,
    label      TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS rooms (
    id       TEXT PRIMARY KEY,
    type     TEXT NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS majors (
    id   INTEGER PRIMARY KEY,
    code TEXT NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS groups (
    id       TEXT PRIMARY KEY,
    major_id INTEGER NOT NULL REFERENCES majors(id),
    course   INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS disciplines (
    id       INTEGER PRIMARY KEY,
    name     TEXT NOT NULL,
    group_id TEXT NOT NULL REFERENCES groups(id),
    period   TEXT NOT NULL,
    is_new   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS topics (
    id            INTEGER PRIMARY KEY,
    discipline_id INTEGER NOT NULL REFERENCES disciplines(id) ON DELETE CASCADE,
    kind          TEXT NOT NULL,
    name          TEXT NOT NULL,
    hours         INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS assignments (
    topic_id       INTEGER PRIMARY KEY REFERENCES topics(id) ON DELETE CASCADE,
    teacher_id     INTEGER NOT NULL REFERENCES teachers(id),
    pairs_per_week INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS lessons (
    id            INTEGER PRIMARY KEY,
    topic_id      INTEGER,
    discipline_id INTEGER,
    group_id      TEXT NOT NULL,
    teacher_id    INTEGER,
    room_id       TEXT,
    kind          TEXT NOT NULL,
    period        TEXT NOT NULL,
    week          INTEGER,
    day           INTEGER,
    slot          INTEGER,
    sub_by        INTEGER,
    pin           INTEGER NOT NULL DEFAULT 0,
    manual        INTEGER NOT NULL DEFAULT 1,
    ni            INTEGER NOT NULL DEFAULT 1,
    nt            INTEGER NOT NULL DEFAULT 1,
    topic_label   TEXT NOT NULL DEFAULT '',
    question      TEXT NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS idx_groups_major ON groups(major_id);
CREATE INDEX IF NOT EXISTS idx_topics_discipline ON topics(discipline_id);
CREATE INDEX IF NOT EXISTS idx_absences_teacher ON absences(teacher_id);
CREATE INDEX IF NOT EXISTS idx_lessons_period ON lessons(period);
CREATE INDEX IF NOT EXISTS idx_lessons_topic ON lessons(topic_id);
"""


def initialize(connection: sqlite3.Connection) -> None:
    """Create every table and index if it does not already exist.

    Args:
        connection: An open connection (see :func:`connection.connect`).
    """
    connection.executescript(SCHEMA)
    connection.commit()
