from pydantic import BaseModel
from typing import Optional

class BookBase(BaseModel):
    title: str
    author: str
    isbn: str
    copies: int
    category: str

class BookCreate(BookBase):
    pass

class Book(BookBase):
    id: int
    available_copies: int

    class Config:
        from_attributes = True

class BookFilter(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    page: int = 1
    limit: int = 10 