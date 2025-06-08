from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from .session import AsyncSessionLocal
from ..models.book import Book
from ..models.student import Student
from ..models.issue import Issue
from datetime import datetime, timedelta, timezone
from sqlalchemy.sql import select

async def init_db():
    print("Starting database initialization...")  # Debug log
    async with AsyncSessionLocal() as session:
        try:
            # Drop tables to ensure a clean slate for development
            print("Dropping existing tables...")
            await drop_tables(session)
            print("Tables dropped successfully.")

            # Create tables
            await create_tables(session)
            print("Tables created successfully")  # Debug log
            
            # Add initial data
            await add_initial_data(session)
            print("Initial data added successfully")  # Debug log
            
            # Verify data
            result = await session.execute(text("SELECT COUNT(*) FROM students"))
            student_count = result.scalar()
            print(f"Total students in database: {student_count}")  # Debug log
            
            result = await session.execute(text("SELECT COUNT(*) FROM books"))
            book_count = result.scalar()
            print(f"Total books in database: {book_count}")  # Debug log
            
        except Exception as e:
            print(f"Error during initialization: {str(e)}")  # Debug log
            raise e

async def drop_tables(session: AsyncSession):
    # Drop tables in correct order (respecting foreign key constraints)
    await session.execute(text("DROP TABLE IF EXISTS issue_details CASCADE"))
    await session.commit()
    
    await session.execute(text("DROP TABLE IF EXISTS issue_header CASCADE"))
    await session.commit()
    
    await session.execute(text("DROP TABLE IF EXISTS issues CASCADE"))
    await session.commit()
    
    await session.execute(text("DROP TABLE IF EXISTS books CASCADE"))
    await session.commit()
    
    await session.execute(text("DROP TABLE IF EXISTS students CASCADE"))
    await session.commit()

async def create_tables(session: AsyncSession):
    print("Creating tables...")  # Debug log
    # Create books table
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            isbn VARCHAR UNIQUE NOT NULL,
            copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL,
            category VARCHAR NOT NULL,
            book_description VARCHAR,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create students table
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            roll_number VARCHAR UNIQUE NOT NULL,
            department VARCHAR NOT NULL,
            semester INTEGER NOT NULL,
            phone VARCHAR UNIQUE NOT NULL,
            email VARCHAR UNIQUE NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    # Create issues table
    await session.execute(text("""
        CREATE TABLE IF NOT EXISTS issues (
            id SERIAL PRIMARY KEY,
            student_id INTEGER NOT NULL,
            book_ids INTEGER[] NOT NULL,
            books_titles VARCHAR NOT NULL,
            issue_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            return_date TIMESTAMP WITHOUT TIME ZONE NOT NULL,
            actual_return_date TIMESTAMP WITHOUT TIME ZONE,
            is_overdue BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """))
    
    await session.commit()
    print("Tables created and committed")  # Debug log

async def add_initial_data(session: AsyncSession):
    """Add initial data to the database."""
    try:
        print("Adding initial data...")
        
        # Check if students already exist
        result = await session.execute(select(Student))
        existing_students = result.scalars().all()
        
        if not existing_students:
            # Add sample students
            students = [
                Student(
                    name="John Doe",
                    roll_number="CS2023001",
                    department="Computer Science",
                    semester=3,
                    phone="1234567890",
                    email="john.doe@example.com"
                ),
                Student(
                    name="Jane Smith",
                    roll_number="CS2023002",
                    department="Computer Science",
                    semester=3,
                    phone="0987654321",
                    email="jane.smith@example.com"
                )
            ]
            session.add_all(students)
            print("Added sample students")
        else:
            print(f"Found {len(existing_students)} existing students, skipping student creation")
        
        # Check if books already exist
        result = await session.execute(select(Book))
        existing_books = result.scalars().all()
        
        if not existing_books:
            # Add sample books
            books = [
                Book(
                    title="The Great Gatsby",
                    author="F. Scott Fitzgerald",
                    isbn="978-0743273565",
                    copies=5,
                    available_copies=5,
                    category="Fiction",
                    book_description="A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan."
                ),
                Book(
                    title="To Kill a Mockingbird",
                    author="Harper Lee",
                    isbn="978-0446310789",
                    copies=3,
                    available_copies=3,
                    category="Fiction",
                    book_description="The story of racial injustice and the loss of innocence in the American South."
                ),
                Book(
                    title="1984",
                    author="George Orwell",
                    isbn="978-0451524935",
                    copies=4,
                    available_copies=4,
                    category="Science Fiction",
                    book_description="A dystopian social science fiction novel and cautionary tale."
                )
            ]
            session.add_all(books)
            print("Added sample books")
        else:
            print(f"Found {len(existing_books)} existing books, skipping book creation")
        
        await session.commit()
        print("Initial data added successfully")
        
    except Exception as e:
        print(f"Error adding initial data: {e}")
        await session.rollback()
        raise e 