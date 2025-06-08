from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
from src.db.session import AsyncSessionLocal
from src.models.issue import Issue
from src.models.student import Student
from src.email_utils import send_email
from sqlalchemy import select
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_and_send_reminders():
    logger.info("Starting reminder check...")
    async with AsyncSessionLocal() as session:
        # Get all active issues (not returned yet)
        result = await session.execute(
            select(Issue).where(Issue.actual_return_date == None)
        )
        issues = result.scalars().all()
        
        for issue in issues:
            # Calculate days until return date
            days_left = (issue.return_date - datetime.now(timezone.utc)).days
            
            # Send reminders for books due in 3 days or less
            if days_left <= 3 and days_left >= 0:
                student_result = await session.execute(
                    select(Student).where(Student.id == issue.student_id)
                )
                student = student_result.scalar_one_or_none()
                
                if student:
                    subject = "Library Book Return Reminder"
                    body = (
                        f"Dear {student.name},\n\n"
                        f"This is a reminder that the book '{issue.book_title}' is due in {days_left} days "
                        f"(due date: {issue.return_date.date()}).\n\n"
                        f"Please return the book on time to avoid any late fees.\n"
                        f"Thank you!"
                    )
                    try:
                        send_email(student.email, subject, body)
                        logger.info(f"Sent reminder to {student.email} for book '{issue.book_title}'")
                    except Exception as e:
                        logger.error(f"Failed to send email to {student.email}: {str(e)}")
    
    logger.info("Reminder check completed")

def start_scheduler():
    scheduler = AsyncIOScheduler()
    # Run the reminder check every day at 9 AM
    scheduler.add_job(check_and_send_reminders, "cron", hour=9, minute=0)
    scheduler.start()
    logger.info("Scheduler started - will check for reminders daily at 9 AM")