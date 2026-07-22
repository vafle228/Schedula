"""SQLite connection factory.

Centralises the pragmas every connection needs (foreign-key enforcement, row
access by column name) so the repositories never have to think about it.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

# In-memory sentinel accepted by :func:`connect` for tests and ephemeral runs.
IN_MEMORY = ":memory:"


def connect(db_path: str | Path) -> sqlite3.Connection:
    """Open a SQLite connection with project-wide settings applied.

    Args:
        db_path: Filesystem path to the database file, or :data:`IN_MEMORY`.

    Returns:
        A connection whose rows are :class:`sqlite3.Row` and with foreign-key
        constraints enforced.
    """
    connection = sqlite3.connect(str(db_path))
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


@contextmanager
def transaction(connection: sqlite3.Connection) -> Iterator[sqlite3.Connection]:
    """Run a block in a transaction, committing on success and rolling back on
    error.

    Args:
        connection: An open connection.

    Yields:
        The same connection, for use inside the ``with`` block.
    """
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
