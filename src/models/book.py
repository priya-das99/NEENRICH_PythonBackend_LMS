from sqlalchemy import Column, String, Integer
from .base import BaseModel

class Book(BaseModel):
    __tablename__ = "books"

    title = Column(String, index=True)
    author = Column(String, index=True)
    isbn = Column(String, unique=True, index=True)
    copies = Column(Integer)
    available_copies = Column(Integer)
    category = Column(String, index=True)
    book_description = Column(String, nullable=True) 