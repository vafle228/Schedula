"""Shared type aliases for the HTTP request/response boundary.

Kept in a dependency-free leaf module so both the dispatcher and the domain
handlers can import it without creating an import cycle between the
``api.routers`` and ``api.handlers`` packages.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from api.errors import ApiError

Params = Mapping[str, str]
Query = Mapping[str, str]
Body = dict[str, Any] | None
Handler = Callable[[Params, Query, Body], Any]


def query_year_id(query: Query) -> int:
    """Return the required ``yearId`` query parameter as an int.

    Raises:
        ApiError: ``400`` when the parameter is missing or non-numeric.
    """
    raw = query.get("yearId")
    if raw is None or not raw.isdigit():
        raise ApiError(400, "Не указан учебный год")
    return int(raw)


def body_year_id(body: dict[str, Any]) -> int:
    """Return the required ``yearId`` field from a request body as an int.

    Raises:
        ApiError: ``400`` when the field is missing or non-numeric.
    """
    raw = body.get("yearId")
    if raw is None:
        raise ApiError(400, "Не указан учебный год")
    return int(raw)
