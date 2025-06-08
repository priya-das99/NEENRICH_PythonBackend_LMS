from sqlalchemy import Column, String, Integer
from .base import BaseModel

class Student(BaseModel):
    __tablename__ = "students"

    name = Column(String, index=True)
    roll_number = Column(String, unique=True, index=True)
    department = Column(String, index=True)
    semester = Column(Integer)
    phone = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True) 