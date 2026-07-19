from enum import StrEnum
from dataclasses import dataclass


class ClassroomKind(StrEnum):
    practice_room = ""
    lecture_room = "Лекционная"



@dataclass
class Classroom:
    id: int | None
    name: str
    kind: ClassroomKind
