from dataclasses import dataclass


@dataclass
class Group:
    id: int | None
    name: str
    course: int
    major_id: int
