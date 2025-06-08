from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int
    available_copies: int
    category: str
    book_description: Optional[str] = None

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IssueBase(BaseModel):
    student_id: int
    book_id: int

class IssueCreate(IssueBase):
    pass

class Issue(IssueBase):
    id: int
    student_name: str
    book_title: str
    issue_date: datetime
    return_date: datetime
    actual_return_date: Optional[datetime] = None
    is_overdue: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IssueReturn(BaseModel):
    issue_id: int 