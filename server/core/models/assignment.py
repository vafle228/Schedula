"""Assignment — links a group's topic to the teacher who will deliver it."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Assignment:
    """A (group, topic) → teacher assignment.

    A topic's plan is shared across every group of its major and course, but the
    teacher is chosen per group — so ИС-31 and ИС-32 can hold different teachers
    for the same shared topic. The aggregate's identity is the ``(group_id,
    topic_id)`` pair.

    Attributes:
        group_id: Group the topic is taught to.
        topic_id: Assigned topic.
        teacher_id: Teacher who will teach the topic to this group.
        pairs_per_week: Auto-derived weekly pair count (``max(1, round(hours /
            2 / weeks_count))``); drives how many lesson slots the pair owns.
    """

    group_id: int
    topic_id: int
    teacher_id: int
    pairs_per_week: int
