"""Schedula backend entry point.

Wires the SQLite persistence, the domain services and the route dispatcher into
a bottle app served under ``/api/v1`` — the exact interface the Vue client
expects once ``USE_MOCK`` is switched off.
"""

from __future__ import annotations

import json
from pathlib import Path

from bottle import Bottle, HTTPResponse, request, response

from api.errors import ApiError
from api.routes import create_dispatcher
from infrastructure.database.seed import seed as seed_database
from infrastructure.database.unit_of_work import SqliteUnitOfWork

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
    "Access-Control-Allow-Headers": (
        "Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token"
    ),
}

API_PREFIX = "/api/v1"
DB_PATH = Path(__file__).resolve().parent / "schedula.db"
_HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]


def handle_options() -> None:
    """Answer CORS preflight requests before routing."""
    if request.method == "OPTIONS":
        raise HTTPResponse(headers=CORS_HEADERS)


def enable_cors() -> None:
    """Attach permissive CORS headers to every response."""
    for key, value in CORS_HEADERS.items():
        response.set_header(key, value)


def _json_response(payload: object) -> str:
    response.content_type = "application/json; charset=utf-8"
    return json.dumps(payload, ensure_ascii=False)


def build_api(uow: SqliteUnitOfWork | None = None) -> Bottle:
    """Assemble the bottle application.

    Args:
        uow: An existing unit of work (for tests). When omitted, one is opened
            on :data:`DB_PATH` and seeded if the database is empty.

    Returns:
        The configured bottle app.
    """
    if uow is None:
        uow = SqliteUnitOfWork(DB_PATH)
        if not uow.periods.list_all():
            seed_database(uow)

    dispatch = create_dispatcher(uow)
    app = Bottle()
    app.add_hook("after_request", enable_cors)
    app.add_hook("before_request", handle_options)

    @app.route(f"{API_PREFIX}/<url:path>", method=_HTTP_METHODS)
    def handle(url: str) -> str:
        try:
            body = request.json
        except (ValueError, TypeError):
            body = None

        full_url = "/" + url
        if request.query_string:
            full_url += "?" + request.query_string

        try:
            result = dispatch(request.method, full_url, body)
        except ApiError as error:
            response.status = error.status
            return _json_response({"error": {"message": error.message}})

        if result is None:
            response.status = 204
            return ""
        return _json_response(result)

    return app


if __name__ == "__main__":
    build_api().run(host="127.0.0.1", port=8000, debug=True)
