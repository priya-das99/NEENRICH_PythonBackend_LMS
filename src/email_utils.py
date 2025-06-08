import smtplib
from email.message import EmailMessage

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg["From"] = "your_gmail@gmail.com"      # <-- Your Gmail address
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    # Gmail SMTP server setup
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    username = "dasp43571@gmail.com"         # <-- Your Gmail address
    password = "aefn iyvk bimq egff"            # <-- Your Gmail App Password

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        print("Email sent successfully!")
