"""Abstract port for workspace-wide bulk operations.

Counting and clearing every aggregate at once is inherently cross-aggregate, so
it lives behind its own narrow port instead of adding a ``delete_all`` to each
of the twelve per-aggregate repositories. Only the onboarding service uses it,
and only to implement the guarded "start from a clean slate" path.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class WorkspaceRepository(ABC):
    """Persistence port for whole-database counting and clearing."""

    @abstractmethod
    def counts(self) -> dict[str, int]:
        """Return the row count of every user-content table, keyed by name."""
        raise NotImplementedError

    @abstractmethod
    def purge(self) -> None:
        """Delete every row of user content in one transaction.

        The lesson-type catalogue is factory data rather than user content and
        is deliberately preserved.
        """
        raise NotImplementedError
