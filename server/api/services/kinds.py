"""Topic-type catalogue helpers shared by the conflict and generator services."""

from __future__ import annotations

from collections.abc import Callable

from core.models.topic_type import TopicType


def make_kind_hours(topic_types: list[TopicType]) -> Callable[[str], int]:
    """Build a resolver from a topic kind to its academic-hour span.

    Mirrors the client's ``kindHours``: an unknown kind falls back to the first
    catalogue entry's span (or 2 when the catalogue is empty).

    Args:
        topic_types: The current topic-type catalogue.

    Returns:
        A function ``kind -> academic hours``.
    """
    mapping = {t.k: t.ac_hours for t in topic_types}
    default = topic_types[0].ac_hours if topic_types else 2
    return lambda kind: mapping.get(kind, default)
