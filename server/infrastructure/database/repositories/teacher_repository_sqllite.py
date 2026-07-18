from server.core.models.teacher import Teacher
from server.core.repositories.teacher_repository import TeacherRepository


class TeacherRepositorySqlLite(TeacherRepository):
    def get_by_id(self, teacher_id: int) -> Teacher:
        pass