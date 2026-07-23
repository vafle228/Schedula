"""Assignment — links a topic to the teacher who will deliver it."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Assignment:
    """A topic → teacher assignment.

    Attributes:
        topic_id: Assigned topic (the aggregate's identity).
        teacher_id: Teacher who will teach the topic.
        pairs_per_week: Auto-derived weekly pair count (``max(1, round(hours /
            2 / weeks_count))``); drives how many lesson slots the topic owns.
    """

    topic_id: int
    teacher_id: int
    pairs_per_week: int
