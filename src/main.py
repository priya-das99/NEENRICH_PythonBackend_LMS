from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.session import engine, Base, AsyncSessionLocal
from src.db.init_db import init_db
from sqlalchemy import text
from src.routers import books, students, issues
from src.scheduler import start_scheduler
import traceback

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("Starting application...")
        # Create tables
        print("Creating database tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Tables created successfully")
        
        # Initialize database with sample data
        print("Initializing database with sample data...")
        await init_db()
        print("Database initialization completed")
        
        # Start the scheduler for reminders
        print("Starting scheduler...")
        start_scheduler()
        print("Scheduler started successfully")
        
        yield
    except Exception as e:
        print("Error during application startup:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
        raise e

app = FastAPI(
    title="Library Management System",
    description="API for managing library books, students, and book issues",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(books.router, prefix="/api/v1/books", tags=["books"])
app.include_router(students.router, prefix="/api/v1/students", tags=["students"])
app.include_router(issues.router, prefix="/api/v1/issues", tags=["issues"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Library Management System",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/check-tables")
async def check_tables():
    async with AsyncSessionLocal() as session:
        # Get list of all tables
        result = await session.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = [row[0] for row in result.fetchall()]
        
        # Get count of records in each table
        table_counts = {}
        for table in tables:
            count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
            count = count_result.scalar()
            table_counts[table] = count
            
        return {
            "tables": tables,
            "record_counts": table_counts
        }

@app.get("/debug/db-state")
async def debug_db_state():
    async with AsyncSessionLocal() as session:
        # Get all students
        result = await session.execute(text("SELECT * FROM students"))
        students = result.fetchall()
        
        # Get all books
        result = await session.execute(text("SELECT * FROM books"))
        books = result.fetchall()
        
        return {
            "students": [dict(student) for student in students],
            "books": [dict(book) for book in books]
        } 