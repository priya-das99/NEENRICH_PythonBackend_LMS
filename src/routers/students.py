from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import List
from ..db.session import get_db
from ..models.student import Student
from ..schemas.student import StudentCreate, Student as StudentSchema, StudentFilter

router = APIRouter()

@router.post("/", response_model=StudentSchema)
async def create_student(student: StudentCreate, db: AsyncSession = Depends(get_db)):
    db_student = Student(**student.dict())
    db.add(db_student)
    await db.commit()
    await db.refresh(db_student)
    return db_student

@router.get("/", response_model=List[StudentSchema])
async def list_students(
    filters: StudentFilter = Depends(),
    db: AsyncSession = Depends(get_db)
):
    query = select(Student)
    
    if filters.department:
        query = query.filter(Student.department == filters.department)
    if filters.semester:
        query = query.filter(Student.semester == filters.semester)
    if filters.search:
        query = query.filter(
            or_(
                Student.name.ilike(f"%{filters.search}%"),
                Student.roll_number.ilike(f"%{filters.search}%"),
                Student.phone.ilike(f"%{filters.search}%")
            )
        )
    
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{student_id}", response_model=StudentSchema)
async def get_student(student_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Student).filter(Student.id == student_id))
    student = result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student 