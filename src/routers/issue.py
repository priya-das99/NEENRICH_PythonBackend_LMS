from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from ..db.session import get_db
from ..models.models import Book, Student, Issue
from ..schemas.issue import IssueCreate, IssueResponse, IssueListResponse
from ..schemas.book import BookResponse
from ..schemas.student import StudentResponse
from ..email_utils import send_overdue_notification

router = APIRouter(
    prefix="/issues",
    tags=["issues"]
)

def get_utc_now():
    return datetime.now(timezone.utc)

@router.post("/issue", response_model=List[IssueResponse])
async def issue_books(issue: IssueCreate, db: AsyncSession = Depends(get_db)):
    # Check if student exists
    student = await db.get(Student, issue.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    # Check if all books exist and are available
    books_to_issue = []
    for book_id in issue.book_ids:
        book = await db.get(Book, book_id)
        if not book:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Book with ID {book_id} not found"
            )
        if book.available_copies <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Book '{book.title}' is not available"
            )
        books_to_issue.append(book)
    
    # Calculate return date (15 days from now)
    return_date = get_utc_now() + timedelta(days=15)
    
    # Create issue records for each book
    issues = []
    for book in books_to_issue:
        issue = Issue(
            student_id=student.id,
            student_name=student.name,
            book_id=book.id,
            book_title=book.title,
            issue_date=get_utc_now(),
            return_date=return_date
        )
        db.add(issue)
        issues.append(issue)
        
        # Update book availability
        book.available_copies -= 1
    
    await db.commit()
    
    # Prepare response
    response = []
    for issue in issues:
        await db.refresh(issue)
        response.append(IssueResponse(
            id=issue.id,
            student=StudentResponse(
                id=student.id,
                name=student.name,
                roll_number=student.roll_number,
                department=student.department,
                semester=student.semester,
                phone=student.phone,
                email=student.email
            ),
            book=BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                copies=book.copies,
                available_copies=book.available_copies,
                category=book.category,
                book_description=book.book_description
            ),
            issue_date=issue.issue_date,
            return_date=issue.return_date,
            actual_return_date=None,
            is_overdue=False
        ))
    
    return response

@router.post("/return/{issue_id}", response_model=IssueResponse)
async def return_book(issue_id: int, db: AsyncSession = Depends(get_db)):
    # Get issue
    issue = await db.get(Issue, issue_id)
    if not issue:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Issue record not found"
        )
    
    if issue.actual_return_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book already returned"
        )
    
    # Update book availability
    book = await db.get(Book, issue.book_id)
    if book:
        book.available_copies += 1
    
    # Update issue
    current_time = get_utc_now()
    issue.actual_return_date = current_time
    issue.is_overdue = current_time > issue.return_date
    
    await db.commit()
    await db.refresh(issue)
    
    # Get student
    student = await db.get(Student, issue.student_id)
    
    # Prepare response
    return IssueResponse(
        id=issue.id,
        student=StudentResponse(
            id=student.id,
            name=student.name,
            roll_number=student.roll_number,
            department=student.department,
            semester=student.semester,
            phone=student.phone,
            email=student.email
        ),
        book=BookResponse(
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            copies=book.copies,
            available_copies=book.available_copies,
            category=book.category,
            book_description=book.book_description
        ),
        issue_date=issue.issue_date,
        return_date=issue.return_date,
        actual_return_date=issue.actual_return_date,
        is_overdue=issue.is_overdue
    )

@router.get("/list", response_model=List[IssueListResponse])
async def list_issues(
    student_id: Optional[int] = None,
    book_id: Optional[int] = None,
    is_overdue: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    # Build query
    query = select(Issue)
    
    if student_id:
        query = query.where(Issue.student_id == student_id)
    
    if book_id:
        query = query.where(Issue.book_id == book_id)
    
    if is_overdue is not None:
        current_time = get_utc_now()
        if is_overdue:
            query = query.where(
                and_(
                    Issue.return_date < current_time,
                    Issue.actual_return_date.is_(None)
                )
            )
        else:
            query = query.where(
                or_(
                    Issue.return_date >= current_time,
                    Issue.actual_return_date.is_not(None)
                )
            )
    
    # Execute query
    result = await db.execute(query)
    issues = result.scalars().all()
    
    # Prepare response
    response = []
    for issue in issues:
        # Get student and book
        student = await db.get(Student, issue.student_id)
        book = await db.get(Book, issue.book_id)
        
        response.append(IssueListResponse(
            id=issue.id,
            student=StudentResponse(
                id=student.id,
                name=student.name,
                roll_number=student.roll_number,
                department=student.department,
                semester=student.semester,
                phone=student.phone,
                email=student.email
            ),
            book=BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                copies=book.copies,
                available_copies=book.available_copies,
                category=book.category,
                book_description=book.book_description
            ),
            issue_date=issue.issue_date,
            return_date=issue.return_date,
            actual_return_date=issue.actual_return_date,
            is_overdue=issue.is_overdue
        ))
    
    return response

@router.get("/overdue", response_model=List[IssueListResponse])
async def get_overdue_books(db: AsyncSession = Depends(get_db)):
    current_time = get_utc_now()
    query = select(Issue).where(
        and_(
            Issue.return_date < current_time,
            Issue.actual_return_date.is_(None)
        )
    )
    
    result = await db.execute(query)
    issues = result.scalars().all()
    
    response = []
    for issue in issues:
        student = await db.get(Student, issue.student_id)
        book = await db.get(Book, issue.book_id)
        
        response.append(IssueListResponse(
            id=issue.id,
            student=StudentResponse(
                id=student.id,
                name=student.name,
                roll_number=student.roll_number,
                department=student.department,
                semester=student.semester,
                phone=student.phone,
                email=student.email
            ),
            book=BookResponse(
                id=book.id,
                title=book.title,
                author=book.author,
                isbn=book.isbn,
                copies=book.copies,
                available_copies=book.available_copies,
                category=book.category,
                book_description=book.book_description
            ),
            issue_date=issue.issue_date,
            return_date=issue.return_date,
            actual_return_date=issue.actual_return_date,
            is_overdue=True
        ))
    
    return response

@router.get("/overdue/notify")
async def notify_overdue_books(db: AsyncSession = Depends(get_db)):
    current_date = get_utc_now()
    overdue_issues = db.query(Issue).filter(
        and_(
            Issue.return_date < current_date,
            Issue.actual_return_date.is_(None)
        )
    ).all()

    for issue in overdue_issues:
        student = db.get(Student, issue.student_id)
        if student:
            overdue_books = [book["book_title"] for book in issue.books_issued 
                           if not book.get("actual_return_date")]
            if overdue_books:
                await send_overdue_notification(student.email, overdue_books)

    return {"message": "Overdue notifications sent"} 