"""Composition root for the SQLite persistence layer.

Opens a single connection, ensures the schema exists, and exposes one ready
repository per aggregate. Application services depend on this object (or the
individual repositories) rather than on ``sqlite3`` directly.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from types import TracebackType

from infrastructure.database.connection import connect
from infrastructure.database.repositories.absence_repository_sqllite import (
    AbsenceRepositorySqlLite,
)
from infrastructure.database.repositories.academic_year_repository_sqllite import (
    AcademicYearRepositorySqlLite,
)
from infrastructure.database.repositories.assignment_repository_sqllite import (
    AssignmentRepositorySqlLite,
)
from infrastructure.database.repositories.discipline_repository_sqllite import (
    DisciplineRepositorySqlLite,
    TopicRepositorySqlLite,
)
from infrastructure.database.repositories.group_repository_sqllite import (
    GroupRepositorySqlLite,
)
from infrastructure.database.repositories.lesson_repository_sqllite import (
    LessonRepositorySqlLite,
)
from infrastructure.database.repositories.major_repository_sqllite import (
    MajorRepositorySqlLite,
)
from infrastructure.database.repositories.room_repository_sqllite import (
    RoomRepositorySqlLite,
)
from infrastructure.database.repositories.settings_repository_sqllite import (
    SettingsRepositorySqlLite,
)
from infrastructure.database.repositories.teacher_repository_sqllite import (
    TeacherRepositorySqlLite,
)
from infrastructure.database.repositories.topic_type_repository_sqllite import (
    TopicTypeRepositorySqlLite,
)
from infrastructure.database.schema import initialize


class SqliteUnitOfWork:
    """Holds the connection and every repository behind it.

    Args:
        db_path: Path to the SQLite file, or ``":memory:"``.
        create_schema: When true (default), run the DDL on construction.
    """

    def __init__(self, db_path: str | Path, *, create_schema: bool = True) -> None:
        self._conn: sqlite3.Connection = connect(db_path)
        if create_schema:
            initialize(self._conn)

        self.settings = SettingsRepositorySqlLite(self._conn)
        self.years = AcademicYearRepositorySqlLite(self._conn)
        self.topic_types = TopicTypeRepositorySqlLite(self._conn)
        self.teachers = TeacherRepositorySqlLite(self._conn)
        self.absences = AbsenceRepositorySqlLite(self._conn)
        self.rooms = RoomRepositorySqlLite(self._conn)
        self.majors = MajorRepositorySqlLite(self._conn)
        self.groups = GroupRepositorySqlLite(self._conn)
        self.disciplines = DisciplineRepositorySqlLite(self._conn)
        self.topics = TopicRepositorySqlLite(self._conn)
        self.assignments = AssignmentRepositorySqlLite(self._conn)
        self.lessons = LessonRepositorySqlLite(self._conn)

    @property
    def connection(self) -> sqlite3.Connection:
        """The underlying connection (for transactions / bulk seeding)."""
        return self._conn

    def commit(self) -> None:
        """Commit the current transaction."""
        self._conn.commit()

    def close(self) -> None:
        """Close the underlying connection."""
        self._conn.close()

    def __enter__(self) -> SqliteUnitOfWork:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.close()
