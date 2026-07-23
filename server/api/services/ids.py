"""Identifier utilities for entity types with non-integer primary keys."""

from __future__ import annotations

import re
from collections.abc import Iterable


def slugify_topic_type(label: str | None, existing_keys: Iterable[str]) -> str:
    """Derive a unique machine key from a topic-type label.

    Mirrors the client's slug rule: lowercase, strip non-alphanumerics, cap at
    six characters, then disambiguate with a numeric suffix.
    """
    base = re.sub(r"[^a-zа-я0-9]+", "", (label or "тип").lower())[:6] or "type"
    taken = set(existing_keys)
    key = base
    counter = 1
    while key in taken:
        counter += 1
        key = f"{base}{counter}"
    return key
