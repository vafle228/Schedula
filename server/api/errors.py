"""Application error type carried across the HTTP boundary."""

from __future__ import annotations


class ApiError(Exception):
    """A domain/HTTP error with a status code and a user-facing message.

    The message is Russian and surfaced verbatim to the client as
    ``{"error": {"message": ...}}`` — matching the mock API contract.
    """

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message
