from pydantic import BaseModel
from typing import Optional

class StudentBase(BaseModel):
    name: str
    roll_number: str
    department: str
    semester: int
    phone: str
    email: str

class StudentCreate(StudentBase):
    pass

class Student(StudentBase):
    id: int

    class Config:
        from_attributes = True

class StudentFilter(BaseModel):
    department: Optional[str] = None
    semester: Optional[int] = None
    search: Optional[str] = None 