from enum import StrEnum
from dataclasses import dataclass


class CourseItemKind(StrEnum):
    pass

@dataclass
class CourseItem:
    id: int | None
    hours_load: int
    kind: CourseItemKind


@dataclass
class Course:
    id: int | None
    name: str
    is_new: bool
    group_id: int

