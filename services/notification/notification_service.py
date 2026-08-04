# services/notification/notification_service.py
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional
import httpx
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class NotificationService:
    """Send notifications via email, push (Firebase), or webhook."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.smtp_config = config.get("smtp", {})
        self.push_config = config.get("push", {})
        self.webhook_config = config.get("webhook", {})

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html: Optional[str] = None,
    ) -> bool:
        """Send email via SMTP."""
        if not self.smtp_config:
            logger.warning("SMTP not configured")
            return False
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_config.get("from_email")
            msg["To"] = to_email

            part1 = MIMEText(body, "plain")
            msg.attach(part1)
            if html:
                part2 = MIMEText(html, "html")
                msg.attach(part2)

            with smtplib.SMTP(
                self.smtp_config.get("host", "localhost"),
                self.smtp_config.get("port", 25)
            ) as server:
                if self.smtp_config.get("use_tls"):
                    server.starttls()
                if self.smtp_config.get("username"):
                    server.login(
                        self.smtp_config["username"],
                        self.smtp_config["password"]
                    )
                server.sendmail(self.smtp_config["from_email"], [to_email], msg.as_string())
            logger.info(f"Email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def send_push_notification(
        self,
        device_token: str,
        title: str,
        body: str,
        data: Optional[Dict] = None,
    ) -> bool:
        """Send push notification via Firebase (placeholder)."""
        # In production, use firebase-admin or similar
        logger.info(f"Push notification to {device_token}: {title} - {body}")
        return True

    async def send_webhook(
        self,
        url: str,
        payload: Dict[str, Any],
    ) -> bool:
        """Send a webhook notification."""
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json=payload, timeout=10.0)
                resp.raise_for_status()
            logger.info(f"Webhook sent to {url}")
            return True
        except Exception as e:
            logger.error(f"Webhook failed: {e}")
            return False