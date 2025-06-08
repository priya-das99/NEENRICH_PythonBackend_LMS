# NETNRICH_PythonBackend_LMS


A FastAPI-based backend system for managing a college library.

## Features

- Book Management (CRUD operations)
- Student Management
- Book Issue and Return System
- Search and Filtering
- Pagination Support
- API Documentation (Swagger UI)

## Tech Stack

- **Backend**: FastAPI (async/await)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Documentation**: FastAPI Swagger UI

## Project Structure

```
library_backend/
├── .env                    # Environment variables
├── .gitignore
├── requirements.txt        # Dependencies
├── README.md              # Project documentation
│
├── src/                   # Main application
│   ├── main.py            # FastAPI app entry point
│   ├── config.py          # App configuration
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic models
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── db/                # Database setup
│   ├── utils/             # Helper functions
│   └── tests/             # Unit tests
│
└── scripts/               # Utility scripts
```

## Setup Instructions

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database and update .env file

4. Run the application:
   ```bash
   uvicorn src.main:app --reload
   ```

## API Documentation

Access the Swagger documentation at http://localhost:8000/docs

## Sample API Usage Examples

### Book Management

#### Create a Book
- **Endpoint**: `POST /books`
- **Request Body**:
  ```json
  {
    "title": "The Great Gatsby",
    "author": "F. Scott Fitzgerald",
    "isbn": "978-0743273565",
    "copies": 5,
    "available_copies": 5,
    "category": "Fiction",
    "description": "A novel about the American Dream."
  }
  ```

#### List All Books
- **Endpoint**: `GET /books`
- **Response**: A list of all books in the library.

#### Get a Specific Book
- **Endpoint**: `GET /books/{id}`
- **Response**: Details of the book with the specified `id`.

### Student Management

#### Create a Student
- **Endpoint**: `POST /students`
- **Request Body**:
  ```json
  {
    "name": "John Doe",
    "roll_number": "12345",
    "department": "Computer Science",
    "semester": 3,
    "phone": "123-456-7890",
    "email": "john.doe@example.com"
  }
  ```

#### List All Students
- **Endpoint**: `GET /students`
- **Response**: A list of all students registered in the library.

#### Get a Specific Student
- **Endpoint**: `GET /students/{id}`
- **Response**: Details of the student with the specified `id`.

### Book Issue and Return

#### Issue a Book
- **Endpoint**: `POST /issues`
- **Request Body**:
  ```json
  {
    "book_id": 1,
    "student_id": 1,
    "return_date": "2023-12-31"
  }
  ```

#### Return a Book
- **Endpoint**: `PUT /issues/{id}/return`
- **Response**: Confirmation of the book return.

#### List All Issues
- **Endpoint**: `GET /issues`
- **Response**: A list of all book issues.

#### Get Overdue Books
- **Endpoint**: `GET /issues/overdue`
- **Response**: A list of all overdue books.

## Database Schema

The database consists of three main tables: `BOOKS`, `STUDENTS`, and `ISSUES`.

### `BOOKS` Table
This table stores information about the books available in the library.
-   `id`: Primary Key, unique identifier for each book.
-   `title`: The title of the book.
-   `author`: The author of the book.
-   `isbn`: Unique identifier for the book (International Standard Book Number).
-   `copies`: Total number of copies of the book in the library.
-   `available_copies`: Number of copies currently available for issue.
-   `category`: Genre or category of the book.
-   `description`: A brief description of the book.
-   `created_at`: Timestamp when the book record was created.
-   `updated_at`: Timestamp when the book record was last updated.

### `STUDENTS` Table
This table stores information about the students registered in the library.
-   `id`: Primary Key, unique identifier for each student.
-   `name`: The full name of the student.
-   `roll_number`: Unique roll number of the student.
-   `department`: The department the student belongs to.
-   `semester`: The current semester of the student.
-   `phone`: Student's phone number.
-   `email`: Student's email address.
-   `created_at`: Timestamp when the student record was created.
-   `updated_at`: Timestamp when the student record was last updated.

### `ISSUES` Table
This table records information about books issued to students. It acts as an associative table for the many-to-many relationship between books and students.
-   `id`: Primary Key, unique identifier for each issue record.
-   `book_id`: Foreign Key referencing the `BOOKS` table (`id` column), indicating which book was issued.
-   `student_id`: Foreign Key referencing the `STUDENTS` table (`id` column), indicating which student issued the book.
-   `issue_date`: The date when the book was issued.
-   `return_date`: The expected date by which the book should be returned.
-   `actual_return_date`: The actual date when the book was returned (NULL if not yet returned).
-   `book_title`: Stores the title of the book at the time of issue for easy retrieval.
-   `student_name`: Stores the name of the student at the time of issue for easy retrieval.
-   `is_overdue`: Boolean flag indicating if the book is currently overdue.
-   `created_at`: Timestamp when the issue record was created.
-   `updated_at`: Timestamp when the issue record was last updated.

### Relationships
-   A `BOOK` can be `ISSUED` multiple times to different `STUDENTS`.
-   A `STUDENT` can `ISSUE` multiple `BOOKS`.
-   The `ISSUES` table links `BOOKS` and `STUDENTS` by storing their respective `id`s as foreign keys, forming a many-to-many relationship.

## ER Diagram

![Hosted Image](https://drive.google.com/file/d/1arz74JphufdhEhPXr-CecHkSHIJ7oga2/view?usp=sharing)
## Bonus Challenges

### 1. Overdue Tracking & Reminder System

#### Design Overview
The system implements an automated overdue book tracking and reminder system using FastAPI BackgroundTasks and APScheduler.

#### Components
1. **Overdue Detection Service**
   - Runs daily to identify books approaching return date
   - Uses APScheduler for scheduled tasks
   - Queries the `issues` table for books:
     - 5 days before return date
     - Currently overdue

2. **Email Reminder System**
   - Sends automated email reminders:
     - First reminder: 5 days before return date
     - Daily reminders: After return date until book is returned
   - Uses FastAPI BackgroundTasks for non-blocking email sending
   - Email content includes:
     - Book details
     - Return date
     - Days overdue (if applicable)
     - Library contact information

3. **Implementation Details**
   ```python
   # Example scheduler setup
   from apscheduler.schedulers.asyncio import AsyncIOScheduler
   from apscheduler.triggers.cron import CronTrigger

   scheduler = AsyncIOScheduler()
   scheduler.add_job(
       check_overdue_books,
       CronTrigger(hour=0, minute=0),  # Run daily at midnight
       id='overdue_check'
   )
   ```

### 2. Flag Overdue Books

#### Implementation
1. **Database Level**
   - Added `is_overdue` boolean field to `issues` table
   - Automatically updated when:
     - Book is returned after due date
     - Daily check for currently overdue books

2. **API Endpoints**
   - Enhanced `/issues/overdue` endpoint to include:
     - Days overdue
     - Overdue status
     - Student contact information
   - Added overdue flag in student's issued books list
   - Added overdue statistics in admin reports

3. **Response Format**
   ```json
   {
     "id": 1,
     "student": {
       "id": 1,
       "name": "John Doe",
       "email": "john@example.com"
     },
     "book": {
       "id": 1,
       "title": "The Great Gatsby"
     },
     "issue_date": "2024-01-01T00:00:00",
     "return_date": "2024-01-15T00:00:00",
     "is_overdue": true,
     "days_overdue": 5
   }
   ```

#### Usage
- Students can view their overdue books in their dashboard
- Librarians can generate reports of all overdue books
- System automatically flags books in API responses
- Email notifications include overdue status and days overdue

#### System Architecture

##### High-Level Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  FastAPI        │     │  PostgreSQL     │     │  Email          │
│  Application    │◄────┤  Database       │     │  Service        │
│                 │     │                 │     │                 │
└────────┬────────┘     └─────────────────┘     └────────┬────────┘
         │                                              │
         │                                              │
         ▼                                              ▼
┌─────────────────┐                          ┌─────────────────┐
│                 │                          │                 │
│  APScheduler    │                          │  Students       │
│  (Background    │                          │  & Librarians   │
│   Tasks)        │                          │                 │
└─────────────────┘                          └─────────────────┘
```

##### Component Details

1. **FastAPI Application Layer**
   - RESTful API endpoints
   - Request validation using Pydantic
   - Authentication and authorization
   - Business logic implementation
   - Database operations through SQLAlchemy

2. **Database Layer (PostgreSQL)**
   - Tables:
     - `books`: Book inventory
     - `students`: Student information
     - `issues`: Book issue records
   - Indexes for optimized queries
   - Foreign key constraints
   - Timestamp tracking

3. **Background Processing Layer**
   - APScheduler for scheduled tasks:
     ```python
     # Scheduler Configuration
     scheduler = AsyncIOScheduler()
     
     # Daily overdue check
     scheduler.add_job(
         check_overdue_books,
         CronTrigger(hour=0, minute=0),
         id='daily_overdue_check'
     )
     
     # Reminder emails
     scheduler.add_job(
         send_reminder_emails,
         CronTrigger(hour=9, minute=0),  # Daily at 9 AM
         id='daily_reminders'
     )
     ```

4. **Email Service Layer**
   - Asynchronous email sending
   - Email templates for:
     - Due date approaching (5 days before)
     - Overdue notifications
     - Return confirmations
   - Rate limiting and queue management

##### Data Flow

1. **Book Issue Process**
   ```
   Student Request → API → Database Check → Issue Book → Update Inventory
   ```

2. **Overdue Detection Process**
   ```
   Scheduler → Check Database → Identify Overdue → Update Flags → Queue Emails
   ```

3. **Reminder System Process**
   ```
   Email Queue → Template Selection → Send Email → Update Notification Status
   ```

##### Security Considerations

1. **Authentication**
   - JWT-based authentication
   - Role-based access control
   - Secure password hashing

2. **Data Protection**
   - Input validation
   - SQL injection prevention
   - XSS protection
   - Rate limiting

3. **Email Security**
   - TLS encryption
   - SPF/DKIM configuration
   - Rate limiting per user

##### Scalability Considerations

1. **Database**
   - Connection pooling
   - Query optimization
   - Indexing strategy

2. **Application**
   - Async/await operations
   - Background task processing
   - Caching strategy

3. **Email Service**
   - Queue-based processing
   - Rate limiting
   - Fallback mechanisms

### 3. Conversational AI Agent

#### Design Overview
A conversational assistant for library administrators that processes natural language queries and provides streaming responses.

#### Components
1. **Webhook API Endpoint**
   ```python
   @router.post("/chat")
   async def chat_endpoint(
       message: ChatMessage,
       conversation_id: str = None
   ):
       # Process natural language query
       # Return streaming response
   ```

2. **Intent Recognition System**
   - Predefined intents for common queries:
     - Overdue books count
     - Department borrowing statistics
     - New books added
     - Book availability
     - Student borrowing history

3. **Query Processing Pipeline**
   - Natural Language Understanding (NLU)
   - Intent classification
   - Entity extraction
   - SQL query generation
   - Response formatting

4. **Context Management**
   - Maintains conversation history
   - Tracks user session
   - Handles follow-up questions

5. **Response Streaming**
   - Real-time response generation
   - Progressive data delivery
   - Typing indicators

#### Example Queries Handled
- "How many books are overdue?"
- "Which department borrowed the most books last month?"
- "How many new books were added this week?"
- "Show me books by author X"
- "What books are currently available?"

#### Implementation Options
1. **OpenAI GPT Integration**
   - Use GPT API for natural language understanding
   - Custom prompt engineering for library context
   - Response streaming using OpenAI's streaming API

2. **Intent-to-Query Mapping**
   - Rule-based intent classification
   - Predefined SQL query templates
   - Custom response formatting

3. **Hybrid Approach**
   - GPT for complex queries
   - Rule-based system for common queries
   - Fallback mechanisms



