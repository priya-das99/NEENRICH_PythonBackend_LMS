from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from ..db.session import get_db
from ..models.book import Book
from ..schemas.book import BookCreate, Book as BookSchema, BookFilter

router = APIRouter()

@router.post("/", response_model=BookSchema)
async def create_book(book: BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = Book(**book.dict(), available_copies=book.copies)
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.get("/", response_model=List[BookSchema])
async def list_books(
    filters: BookFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Book)
    
    if filters.title:
        query = query.filter(Book.title.ilike(f"%{filters.title}%"))
    if filters.author:
        query = query.filter(Book.author.ilike(f"%{filters.author}%"))
    if filters.category:
        query = query.filter(Book.category == filters.category)
    
    query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{book_id}", response_model=BookSchema)
async def get_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).filter(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{book_id}", response_model=BookSchema)
async def update_book(
    book_id: int,
    book_update: BookCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Book).filter(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    for key, value in book_update.dict().items():
        setattr(book, key, value)
    
    await db.commit()
    await db.refresh(book)
    return book

@router.delete("/{book_id}")
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Book).filter(Book.id == book_id))
    book = result.scalar_one_or_none()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    await db.delete(book)
    await db.commit()
    return {"message": "Book deleted successfully"} 