from dataclasses import dataclass


@dataclass
class Teacher:
    id: int | None
    full_name: str
    job_title: str
    photo_base64: str
    
