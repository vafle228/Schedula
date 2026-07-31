"""First-run onboarding state — a single, year-independent row.

Tracks how far the user got through the guided tour so it can be resumed after
a restart, and carries the provenance markers (``demo_seeded`` +
``seed_counts``) that let the service decide whether the bundled demo dataset
is still untouched and may therefore be wiped. Once the user has edited
anything, the counts stop matching and the destructive "start clean" path is
closed permanently — replaying the tour never touches data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class OnboardingStatus(StrEnum):
    """Lifecycle of the guided tour."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class DataChoice(StrEnum):
    """What the user picked on the welcome screen."""

    DEMO = "demo"
    CLEAN = "clean"


@dataclass(slots=True)
class OnboardingState:
    """Progress through the first-run tour.

    Attributes:
        status: Where the user is in the tour lifecycle.
        version: Tour content version this progress belongs to; bumping it in
            :data:`TOUR_VERSION` lets a future release re-offer the tour.
        current_step: Id of the step to resume on; empty before the first run.
        completed_steps: Ids of the steps already seen, in visit order.
        data_choice: ``demo`` / ``clean`` once the welcome screen is resolved.
        demo_seeded: True when this database was created by the demo seeder —
            the only case in which nothing in it is user-authored.
        seed_counts: Row counts captured right after seeding; a mismatch proves
            the user has since edited the data.
        updated_at: ISO-8601 timestamp of the last write.
    """

    status: OnboardingStatus = OnboardingStatus.PENDING
    version: int = 1
    current_step: str = ""
    completed_steps: list[str] = field(default_factory=list)
    data_choice: DataChoice | None = None
    demo_seeded: bool = False
    seed_counts: dict[str, int] = field(default_factory=dict)
    updated_at: str = ""


TOUR_VERSION: int = 1
"""Content version of the shipped tour; stored on every progress write."""


def default_onboarding() -> OnboardingState:
    """Build the state a database without an ``onboarding`` row implies.

    Returns:
        A pending state with ``demo_seeded`` false — an existing installation
        upgrading to this build gets the tour but never the wipe option.
    """
    return OnboardingState(status=OnboardingStatus.PENDING, version=TOUR_VERSION)
