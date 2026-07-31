"""Application service for the first-run onboarding tour.

Two responsibilities that must not bleed into each other:

* **Tour progress** — read/patch/restart. Entirely non-destructive, so the user
  can replay the tour at any time without risking a byte of their data.
* **"Start from a clean slate"** — the single destructive path, offered only on
  the very first launch of a freshly seeded database.

The wipe is guarded by three independent conditions (see
:meth:`OnboardingService._may_start_clean`). The decisive one is the seed
fingerprint: :func:`infrastructure.database.seed.seed` records the row counts it
produced, and any subsequent edit — one added teacher, one deleted group — makes
the live counts diverge and closes the wipe path permanently. An installation
that predates this feature has no onboarding row at all, so ``demo_seeded`` is
false and the path is closed by construction.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from api.errors import ApiError
from api.services.base import ServiceBase
from api.services.years import YearService
from core.models.academic_year import AcademicYear
from core.models.onboarding import (
    TOUR_VERSION,
    DataChoice,
    OnboardingState,
    OnboardingStatus,
    default_onboarding,
)
from core.repositories.onboarding_repository import OnboardingRepository
from core.repositories.workspace_repository import WorkspaceRepository


class OnboardingService(ServiceBase):
    """Read and advance the tour; optionally reset the workspace on first run."""

    def __init__(
        self,
        onboarding: OnboardingRepository,
        workspace: WorkspaceRepository,
        years: YearService,
    ) -> None:
        self._onboarding = onboarding
        self._workspace = workspace
        self._years = years

    def get(self) -> OnboardingState:
        """Return the stored state, or the implied default when never written.

        The default is *not* persisted — writing it here would make every read
        look like a first run that had already been resolved.
        """
        return self._onboarding.get() or default_onboarding()

    def may_start_clean(self) -> bool:
        """Whether the demo dataset may still be wiped."""
        return self._may_start_clean(self.get())

    def patch(self, changes: Mapping[str, Any]) -> OnboardingState:
        """Apply ``changes`` to the tour progress and persist it."""
        state = self.get()
        self._apply(state, changes)
        return self._store(state)

    def restart(self) -> OnboardingState:
        """Rewind the tour to its first step without touching any user data."""
        state = self.get()
        state.status = OnboardingStatus.IN_PROGRESS
        state.current_step = ""
        state.completed_steps = []
        return self._store(state)

    def start_clean(self) -> AcademicYear:
        """Wipe the untouched demo dataset and create an empty active year.

        Returns:
            The freshly created, activated academic year.

        Raises:
            ApiError: ``409`` when anything suggests the database holds real
                user content.
        """
        state = self.get()
        if not self._may_start_clean(state):
            raise ApiError(409, "В базе уже есть ваши данные — очистка отменена")

        self._workspace.purge()
        year = self._fresh_year()

        state.data_choice = DataChoice.CLEAN
        state.demo_seeded = False
        state.seed_counts = {}
        state.status = OnboardingStatus.IN_PROGRESS
        self._store(state)
        return year

    def _may_start_clean(self, state: OnboardingState) -> bool:
        """All three guards must hold; see the module docstring."""
        return (
            state.status == OnboardingStatus.PENDING
            and state.demo_seeded
            and state.seed_counts == self._workspace.counts()
        )

    def _fresh_year(self) -> AcademicYear:
        """Create and activate an empty academic year for the current season."""
        today = datetime.now(UTC)
        # Before September the current academic year began the previous autumn.
        start = today.year if today.month >= 9 else today.year - 1
        year = self._years.create(
            name=f"{start}/{str(start + 1)[-2:]}",
            aut_from=f"01.09.{start}",
            aut_to=f"31.12.{start}",
            spr_from=f"09.01.{start + 1}",
            spr_to=f"30.06.{start + 1}",
        )
        # ``activate`` flips statuses in storage; re-read so the caller sees it.
        activated = self._years.activate(year.id)
        return next(y for y in activated if y.id == year.id)

    def _store(self, state: OnboardingState) -> OnboardingState:
        state.version = TOUR_VERSION
        state.updated_at = datetime.now(UTC).isoformat(timespec="seconds")
        self._onboarding.save(state)
        return state
