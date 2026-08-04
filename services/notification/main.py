# services/notification/main.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel, EmailStr
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = FastAPI(title="Notification Service", version="1.0.0")
logger = logging.getLogger(__name__)

class NotificationRequest(BaseModel):
    recipient: str  # email or phone
    subject: str
    message: str
    channel: str = "email"  # email, sms, push

@app.post("/send")
async def send_notification(request: NotificationRequest, background_tasks: BackgroundTasks):
    """Send a notification via the specified channel."""
    background_tasks.add_task(_send_email, request.recipient, request.subject, request.message)
    return {"status": "queued", "recipient": request.recipient}

def _send_email(recipient: str, subject: str, message: str):
    """Send email using SMTP (configure via env)."""
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")
    if not smtp_user or not smtp_pass:
        logger.error("SMTP credentials not configured")
        return
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_user
        msg["To"] = recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, recipient, msg.as_string())
        logger.info(f"Email sent to {recipient}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)