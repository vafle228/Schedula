"""Regex mini-router and request dispatcher.

A faithful port of the client's mock ``server.js`` router: each route maps a
``method + pattern`` to a handler. ``:name`` segments in a pattern are captured
and handed to the handler as ``params``. The class-based :class:`Router` is the
registration surface shared by every ``register_*_routes`` module, and its
:meth:`Router.dispatch` is what ``main.py`` drives with ``(method, url, body)``.
"""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import unquote

from api.errors import ApiError
from api.http_types import Body, Handler


class _Route:
    """A single compiled ``method + pattern`` entry bound to its handler."""

    __slots__ = ("method", "regex", "keys", "handler")

    def __init__(self, method: str, pattern: str, handler: Handler) -> None:
        keys: list[str] = []

        def _capture(match: re.Match[str]) -> str:
            keys.append(match.group(0)[1:])
            return "([^/]+)"

        self.method = method
        self.regex = re.compile("^" + re.sub(r":[^/]+", _capture, pattern) + "$")
        self.keys = keys
        self.handler = handler


class Router:
    """Collects routes and resolves an incoming request to a handler call."""

    def __init__(self) -> None:
        self._routes: list[_Route] = []

    def on(self, method: str, pattern: str, handler: Handler) -> None:
        """Register ``handler`` for ``method`` requests matching ``pattern``.

        Args:
            method: The HTTP verb (``"GET"``, ``"POST"`` …).
            pattern: A path template where ``:name`` segments become params.
            handler: Callable invoked with ``(params, query, body)``.
        """
        self._routes.append(_Route(method, pattern, handler))

    def dispatch(self, method: str, url: str, body: Body) -> Any:
        """Route ``method``/``url`` to its handler and return the result.

        Args:
            method: The HTTP verb of the request.
            url: The path, optionally followed by a ``?query`` string.
            body: The parsed JSON request body, if any.

        Returns:
            The handler's (json-serializable) result, or ``None`` for 204.

        Raises:
            ApiError: ``404`` when no route matches; handlers raise their own.
        """
        path, _, query_string = url.partition("?")
        query = self._parse_query(query_string)
        for route in self._routes:
            if route.method != method:
                continue
            match = route.regex.match(path)
            if match is None:
                continue
            params = {
                key: unquote(match.group(index + 1))
                for index, key in enumerate(route.keys)
            }
            return route.handler(params, query, body)
        raise ApiError(404, f"{method} {path} — маршрут не найден")

    @staticmethod
    def _parse_query(query_string: str) -> dict[str, str]:
        query: dict[str, str] = {}
        if not query_string:
            return query
        for pair in query_string.split("&"):
            key, _, value = pair.partition("=")
            query[unquote(key)] = unquote(value)
        return query
