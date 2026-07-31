"""SQLite adapter for :class:`OnboardingRepository`."""

from __future__ import annotations

import json
import sqlite3

from core.models.onboarding import DataChoice, OnboardingState, OnboardingStatus
from core.repositories.onboarding_repository import OnboardingRepository

_SINGLETON_ID = 1


def _row_to_state(row: sqlite3.Row) -> OnboardingState:
    choice = row["data_choice"]
    return OnboardingState(
        status=OnboardingStatus(row["status"]),
        version=row["version"],
        current_step=row["current_step"],
        completed_steps=json.loads(row["completed_steps"]),
        data_choice=DataChoice(choice) if choice else None,
        demo_seeded=bool(row["demo_seeded"]),
        seed_counts=json.loads(row["seed_counts"]),
        updated_at=row["updated_at"],
    )


class OnboardingRepositorySqlLite(OnboardingRepository):
    """Stores the single onboarding row, JSON-encoding its list/dict fields."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._conn = connection

    def get(self) -> OnboardingState | None:
        row = self._conn.execute(
            "SELECT * FROM onboarding WHERE id = ?", (_SINGLETON_ID,)
        ).fetchone()
        return _row_to_state(row) if row else None

    def save(self, state: OnboardingState) -> None:
        self._conn.execute(
            """
            INSERT INTO onboarding (id, status, version, current_step,
                                    completed_steps, data_choice, demo_seeded,
                                    seed_counts, updated_at)
            VALUES (:id, :status, :version, :current_step,
                    :completed_steps, :data_choice, :demo_seeded,
                    :seed_counts, :updated_at)
            ON CONFLICT(id) DO UPDATE SET
                status = excluded.status,
                version = excluded.version,
                current_step = excluded.current_step,
                completed_steps = excluded.completed_steps,
                data_choice = excluded.data_choice,
                demo_seeded = excluded.demo_seeded,
                seed_counts = excluded.seed_counts,
                updated_at = excluded.updated_at
            """,
            {
                "id": _SINGLETON_ID,
                "status": str(state.status),
                "version": state.version,
                "current_step": state.current_step,
                "completed_steps": json.dumps(state.completed_steps),
                "data_choice": str(state.data_choice) if state.data_choice else None,
                "demo_seeded": int(state.demo_seeded),
                "seed_counts": json.dumps(state.seed_counts),
                "updated_at": state.updated_at,
            },
        )
        self._conn.commit()
