"""Abstract port for onboarding-state persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod

from core.models.onboarding import OnboardingState


class OnboardingRepository(ABC):
    """Persistence port for the single :class:`OnboardingState` row."""

    @abstractmethod
    def get(self) -> OnboardingState | None:
        """Return the stored state, or ``None`` when it was never written."""
        raise NotImplementedError

    @abstractmethod
    def save(self, state: OnboardingState) -> None:
        """Insert or replace the singleton state row (upsert)."""
        raise NotImplementedError
