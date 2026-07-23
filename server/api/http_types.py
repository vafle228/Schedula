"""Shared type aliases for the HTTP request/response boundary.

Kept in a dependency-free leaf module so both the dispatcher and the domain
handlers can import it without creating an import cycle between the
``api.routers`` and ``api.handlers`` packages.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

Params = Mapping[str, str]
Query = Mapping[str, str]
Body = dict[str, Any] | None
Handler = Callable[[Params, Query, Body], Any]
