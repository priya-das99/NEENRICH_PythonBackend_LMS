from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from ..db.session import get_db
from ..models.issue import Issue
from ..models.book import Book
from ..models.student import Student
from ..schemas.issue import IssueCreate, Issue as IssueSchema, StudentIssue, AdminIssue
from src.scheduler import start_scheduler

router = APIRouter()

@router.post("/issue", response_model=IssueSchema, status_code=status.HTTP_201_CREATED)
async def issue_book(issue_data: IssueCreate, db: AsyncSession = Depends(get_db)):
    # Check if student exists
    student = await db.scalar(select(Student).where(Student.id == issue_data.student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    # Determine the list of book_ids based on input
    if issue_data.book_id is not None:
        incoming_book_ids = [issue_data.book_id]
    elif issue_data.book_ids is not None:
        incoming_book_ids = issue_data.book_ids
    else:
        raise HTTPException(status_code=400, detail="Either book_id or book_ids must be provided.")

    # Generate timezone-naive issue and return dates
    issue_date_naive = datetime.now().replace(tzinfo=None)
    return_date_naive = (datetime.now() + timedelta(days=14)).replace(tzinfo=None)

    # Try to find an existing issue record for the student on the same day
    # We need to consider the start and end of the day for comparison
    start_of_day = issue_date_naive.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1, microseconds=-1)

    existing_issue = await db.scalar(
        select(Issue).where(
            Issue.student_id == issue_data.student_id,
            Issue.issue_date >= start_of_day,
            Issue.issue_date <= end_of_day,
            Issue.actual_return_date == None # Only consider active issues
        )
    )

    # Validate and prepare books
    books_to_issue = []
    book_titles = []
    for book_id in incoming_book_ids:
        book = await db.scalar(select(Book).where(Book.id == book_id))
        if not book:
            raise HTTPException(status_code=404, detail=f"Book with ID {book_id} not found")
        if book.available_copies <= 0:
            raise HTTPException(status_code=400, detail=f"Book with ID {book_id} not available")
        books_to_issue.append(book)
        book_titles.append(book.title)

    if existing_issue:
        # Update existing issue record
        print(f"Updating existing issue record for student {student.id} on {issue_date_naive.date()}")
        existing_issue.book_ids.extend(incoming_book_ids)
        existing_issue.books_titles = ", ".join(sorted(list(set(existing_issue.books_titles.split(', ') + book_titles))))
        existing_issue.updated_at = datetime.now().replace(tzinfo=None)
        db.add(existing_issue)
        issued_record = existing_issue
    else:
        # Create new issue record
        print(f"Creating new issue record for student {student.id} on {issue_date_naive.date()}")
        issued_record = Issue(
            student_id=issue_data.student_id,
            book_ids=incoming_book_ids,
            books_titles=", ".join(sorted(book_titles)),
            issue_date=issue_date_naive,
            return_date=return_date_naive,
            is_overdue=False
        )
        db.add(issued_record)

    # Update book availability
    for book in books_to_issue:
        book.available_copies -= 1
        db.add(book)

    await db.commit()
    await db.refresh(issued_record)
    
    # To ensure relationships are loaded for response_model, manually fetch details
    # Note: This is a workaround since `relationship` on `student` in Issue model 
    # doesn't auto-populate if student_id is not a ForeignKey with `use_alter=True` or `_sa_skip_dependent_arguments=True`
    # which would require more complex migrations. For simplicity, we load it here.
    issued_record.student = student

    return issued_record

@router.put("/{issue_id}/return/{book_id}", response_model=IssueSchema)
async def return_book(issue_id: int, book_id: int, db: AsyncSession = Depends(get_db)):
    issue = await db.scalar(select(Issue).where(Issue.id == issue_id))
    if not issue:
        raise HTTPException(status_code=404, detail="Issue record not found")

    if book_id not in issue.book_ids:
        raise HTTPException(status_code=400, detail=f"Book with ID {book_id} was not issued in this record.")

    # Remove book from the issue record
    issue.book_ids.remove(book_id)
    
    # Reconstruct books_titles
    current_book_titles = issue.books_titles.split(', ')
    book_to_remove_title = None
    
    # Fetch the actual book title from the database to ensure correctness
    book_obj = await db.scalar(select(Book).where(Book.id == book_id))
    if book_obj:
        book_to_remove_title = book_obj.title

    if book_to_remove_title and book_to_remove_title in current_book_titles:
        current_book_titles.remove(book_to_remove_title)
    issue.books_titles = ", ".join(sorted(current_book_titles))

    # Update actual_return_date only if all books are returned from this issue
    if not issue.book_ids: # If no books left in the array
        issue.actual_return_date = datetime.now().replace(tzinfo=None)
        issue.is_overdue = (issue.actual_return_date > issue.return_date)

    issue.updated_at = datetime.now().replace(tzinfo=None)
    db.add(issue)

    # Update book availability
    book = await db.scalar(select(Book).where(Book.id == book_id))
    if book:
        book.available_copies += 1
        db.add(book)

    await db.commit()
    await db.refresh(issue)

    # To ensure relationships are loaded for response_model, manually fetch details
    issue.student = await db.scalar(select(Student).where(Student.id == issue.student_id))

    return issue

@router.get("/student/{student_id}", response_model=List[StudentIssue])
async def get_student_issues(student_id: int, db: AsyncSession = Depends(get_db)):
    student = await db.scalar(select(Student).where(Student.id == student_id))
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    result = await db.execute(
        select(Issue).where(
            Issue.student_id == student_id
        ).order_by(Issue.issue_date.desc())
    )
    issues = result.scalars().all()

    current_time_utc = datetime.now(timezone.utc)
    student_issues = []

    for issue in issues:
        # Convert return_date to timezone-aware for calculation if it's naive
        issue_return_date_aware = issue.return_date.replace(tzinfo=timezone.utc) if issue.return_date.tzinfo is None else issue.return_date
        
        days_left = (issue_return_date_aware - current_time_utc).days
        is_overdue = days_left < 0 and issue.actual_return_date is None

        student_issue = StudentIssue(
            id=issue.id,
            student_id=issue.student_id,
            book_ids=issue.book_ids,
            books_titles=issue.books_titles,
            issue_date=issue.issue_date,
            return_date=issue.return_date,
            actual_return_date=issue.actual_return_date,
            is_overdue=is_overdue,
            days_remaining=abs(days_left) if not is_overdue and issue.actual_return_date is None else None,
            # Manual assignment of student object for the response model
            student=student 
        )
        student_issues.append(student_issue)

    return student_issues

@router.get("/overdue", response_model=List[AdminIssue])
async def get_overdue_books(db: AsyncSession = Depends(get_db)):
    current_time_utc = datetime.now(timezone.utc)
    
    result = await db.execute(
        select(Issue).where(
            Issue.actual_return_date == None,
            Issue.return_date < current_time_utc.replace(tzinfo=None) # Compare naive dates
        )
    )
    issues = result.scalars().all()

    overdue_issues = []
    for issue in issues:
        # Convert return_date to timezone-aware for calculation if it's naive
        issue_return_date_aware = issue.return_date.replace(tzinfo=timezone.utc) if issue.return_date.tzinfo is None else issue.return_date
        days_overdue = (current_time_utc - issue_return_date_aware).days

        # Fetch student for the response model
        student = await db.scalar(select(Student).where(Student.id == issue.student_id))
        if not student: # Should not happen if data integrity is maintained
            continue 

        admin_issue = AdminIssue(
            id=issue.id,
            student_id=issue.student_id,
            book_ids=issue.book_ids,
            books_titles=issue.books_titles,
            issue_date=issue.issue_date,
            return_date=issue.return_date,
            actual_return_date=issue.actual_return_date,
            is_overdue=True,
            days_overdue=days_overdue,
            # Manual assignment of student object for the response model
            student=student 
        )
        overdue_issues.append(admin_issue)

    return overdue_issues 