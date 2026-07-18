from abc import ABC, abstractmethod

from server.core.models.teacher import Teacher


class TeacherRepository(ABC):
    @abstractmethod
    def get_by_id(self, teacher_id: int) -> Teacher:
        raise NotImplementedError
