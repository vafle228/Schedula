from dataclasses import dataclass


@dataclass
class Group:
    id: int | None
    name: str