"""Abstract port for semester-settings persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.settings import SemesterSettings


class SettingsRepository(ABC):
    """Persistence port for :class:`SemesterSettings` aggregates."""

    @abstractmethod
    def list_by_year(self, year_id: int) -> list[SemesterSettings]:
        """Return the year's settings, autumn first then spring."""
        raise NotImplementedError

    @abstractmethod
    def get(self, year_id: int, period: str) -> SemesterSettings | None:
        """Return the settings for ``(year_id, period)`` or ``None``."""
        raise NotImplementedError

    @abstractmethod
    def save(self, settings: SemesterSettings) -> None:
        """Insert or replace ``settings`` (upsert by ``(year_id, period)``)."""
        raise NotImplementedError

    @abstractmethod
    def delete_for_year(self, year_id: int) -> None:
        """Remove every settings row of ``year_id`` (no-op if absent)."""
        raise NotImplementedError
