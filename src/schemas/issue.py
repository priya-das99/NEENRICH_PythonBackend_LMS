from pydantic import BaseModel, model_validator
from datetime import datetime
from typing import List, Optional
from .book import Book as BookSchema
from .student import Student as StudentSchema

class IssueBase(BaseModel):
    student_id: int

class IssueCreate(IssueBase):
    book_id: Optional[int] = None
    book_ids: Optional[List[int]] = None

    @model_validator(mode='after')
    def check_book_fields(self):
        if self.book_id is None and (self.book_ids is None or len(self.book_ids) == 0):
            raise ValueError("Either book_id or at least one book_id in book_ids must be provided")
        if self.book_id is not None and self.book_ids is not None and len(self.book_ids) > 0:
            raise ValueError("Cannot provide both book_id and book_ids")
        return self

class IssueResponse(BaseModel):
    id: int
    student: StudentSchema
    issue_date: datetime
    return_date: datetime
    actual_return_date: Optional[datetime] = None
    is_overdue: bool
    book_ids: List[int]
    books_titles: str

class IssueListResponse(BaseModel):
    id: int
    student: StudentSchema
    issue_date: datetime
    return_date: datetime
    actual_return_date: Optional[datetime] = None
    is_overdue: bool
    book_ids: List[int]
    books_titles: str

class Issue(IssueBase):
    id: int
    book_ids: List[int]
    books_titles: str
    issue_date: datetime
    return_date: datetime
    actual_return_date: Optional[datetime] = None
    is_overdue: bool = False

    class Config:
        from_attributes = True

class StudentIssue(Issue):
    days_remaining: Optional[int] = None

    class Config:
        from_attributes = True

class AdminIssue(Issue):
    days_overdue: Optional[int] = None

    class Config:
        from_attributes = True