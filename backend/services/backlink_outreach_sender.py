"""Email sender for backlink outreach via SMTP."""

from __future__ import annotations

import os
import ssl
import smtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")
SMTP_VERIFY_TLS = os.getenv("SMTP_VERIFY_TLS", "true").lower() in ("true", "1", "yes")
SMTP_SEND_TIMEOUT = int(os.getenv("SMTP_SEND_TIMEOUT", "30"))


class BacklinkOutreachSender:
    def __init__(self):
        self._host = SMTP_HOST
        self._port = SMTP_PORT
        self._username = SMTP_USERNAME
        self._password = SMTP_PASSWORD
        self._from_email = SMTP_FROM_EMAIL or SMTP_USERNAME
        self._use_tls = SMTP_USE_TLS
        self._verify_tls = SMTP_VERIFY_TLS
        self._timeout = SMTP_SEND_TIMEOUT

    def is_configured(self) -> bool:
        return bool(self._username and self._password)

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        from_email: Optional[str] = None,
    ) -> bool:
        if not self.is_configured():
            logger.error("SMTP not configured: set SMTP_USERNAME and SMTP_PASSWORD")
            return False

        sender = from_email or self._from_email

        msg = MIMEMultipart("alternative")
        msg["From"] = sender
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        loop = asyncio.get_running_loop()

        def _send() -> bool:
            try:
                tls_context = ssl.create_default_context()
                if not self._verify_tls:
                    tls_context.check_hostname = False
                    tls_context.verify_mode = ssl.CERT_NONE
                with smtplib.SMTP(self._host, self._port, timeout=self._timeout) as server:
                    if self._use_tls:
                        server.starttls(context=tls_context)
                        server.ehlo()
                    server.login(self._username, self._password)
                    server.sendmail(sender, [to_email], msg.as_string())
                logger.info(f"Email sent to {to_email}: {subject[:60]}")
                return True
            except smtplib.SMTPException as e:
                logger.error(f"SMTP error sending to {to_email}: {e}")
                return False
            except Exception as e:
                logger.error(f"Unexpected error sending to {to_email}: {e}")
                return False

        return await loop.run_in_executor(None, _send)

    def personalize(self, template: str, variables: dict) -> str:
        """Replace {placeholder} variables in a template string."""
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template


backlink_outreach_sender = BacklinkOutreachSender()