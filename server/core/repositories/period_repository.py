"""Abstract port for period (semester) persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.period import Period


class PeriodRepository(ABC):
    """Persistence port for :class:`Period` aggregates."""

    @abstractmethod
    def list_all(self) -> list[Period]:
        """Return every period, autumn first then spring."""
        raise NotImplementedError

    @abstractmethod
    def get(self, period_id: str) -> Period | None:
        """Return the period with ``period_id`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def save(self, period: Period) -> None:
        """Insert or replace ``period`` (upsert by id)."""
        raise NotImplementedError
