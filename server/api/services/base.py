"""Shared base for the domain service classes.

Services own the application's business rules and reach persistence only through
the abstract repository ports (:mod:`core.repositories`), never through a
concrete implementation. Domain/HTTP failures are signalled with
:class:`api.errors.ApiError`, which the transport layer maps to a status code.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from api.errors import ApiError

T = TypeVar("T")


class ServiceBase:
    """Common guard helpers shared by every domain service."""

    @staticmethod
    def _apply(entity: object, changes: Mapping[str, Any]) -> None:
        """Assign each ``field -> value`` in ``changes`` onto ``entity``.

        Callers pass only the fields present in the request, already translated
        to the entity's own attribute names, so a plain attribute write is the
        correct partial-update semantics.
        """
        for field, value in changes.items():
            setattr(entity, field, value)

    @staticmethod
    def _require(entity: T | None, message: str) -> T:
        """Return ``entity`` or raise a ``404`` :class:`ApiError`.

        Args:
            entity: The looked-up entity, possibly ``None``.
            message: The Russian, user-facing message for the 404.

        Returns:
            The non-``None`` entity.

        Raises:
            ApiError: ``404`` when ``entity`` is ``None``.
        """
        if entity is None:
            raise ApiError(404, message)
        return entity
