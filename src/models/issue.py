from sqlalchemy import Column, Integer, DateTime, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from .base import BaseModel

class Issue(BaseModel):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    book_ids = Column(ARRAY(Integer), nullable=False)
    books_titles = Column(String, nullable=False)
    issue_date = Column(DateTime)
    return_date = Column(DateTime)
    actual_return_date = Column(DateTime, nullable=True)
    is_overdue = Column(Boolean, default=False)

    student = relationship("Student") 