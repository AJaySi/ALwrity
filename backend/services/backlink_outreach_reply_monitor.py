"""IMAP-based reply monitoring for backlink outreach."""

from __future__ import annotations

import os
import asyncio
import imaplib
import email as email_lib
from email.utils import parsedate_to_datetime
from typing import List, Optional
from loguru import logger


IMAP_HOST = os.getenv("IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("IMAP_PORT", "993"))
IMAP_USERNAME = os.getenv("IMAP_USERNAME", "")
IMAP_PASSWORD = os.getenv("IMAP_PASSWORD", "")
IMAP_FOLDER = os.getenv("IMAP_FOLDER", "INBOX")
IMAP_FETCH_LIMIT = int(os.getenv("IMAP_FETCH_LIMIT", "50"))

# Search keywords for auto-classification
INTERESTED_KEYWORDS = [
    "interested", "let's discuss", "sounds good", "would love to", "yes",
    "sure", "tell me more", "looks good", "happy to", "let's do it",
    "sign me up", "count me in", "proceed", "approved",
]
NOT_INTERESTED_KEYWORDS = [
    "not interested", "unsubscribe", "no thanks", "remove me", "stop",
    "don't contact", "spam", "not relevant", "no longer interested",
    "please stop", "do not email",
]
OUT_OF_OFFICE_KEYWORDS = [
    "out of office", "vacation", "on leave", "away from", "return on",
    "not in the office", "will be back",
]


class BacklinkOutreachReplyMonitor:
    def __init__(self):
        self._host = IMAP_HOST
        self._port = IMAP_PORT
        self._username = IMAP_USERNAME
        self._password = IMAP_PASSWORD
        self._folder = IMAP_FOLDER
        self._fetch_limit = IMAP_FETCH_LIMIT

    def is_configured(self) -> bool:
        return bool(self._username and self._password)

    async def poll_replies(self, sent_from_email: str) -> List[dict]:
        """Poll IMAP inbox for replies to a specific sender address."""
        if not self.is_configured():
            logger.warning("IMAP not configured: set IMAP_USERNAME and IMAP_PASSWORD")
            return []

        loop = asyncio.get_running_loop()

        def _poll() -> List[dict]:
            try:
                mail = imaplib.IMAP4_SSL(self._host, self._port)
                mail.login(self._username, self._password)
                mail.select(self._folder)

                safe_email = sent_from_email.replace('"', "").replace("\\", "")
                search_criteria = f'(TO "{safe_email}")'
                status, message_ids = mail.search(None, search_criteria)
                if status != "OK":
                    return []

                ids = message_ids[0].split() if message_ids[0] else []
                if not ids:
                    return []

                ids = ids[-self._fetch_limit:]

                replies = []
                for mid in ids:
                    status, msg_data = mail.fetch(mid, "(RFC822)")
                    if status != "OK":
                        continue

                    raw_email = msg_data[0][1] if msg_data else None
                    if not raw_email:
                        continue

                    parsed = email_lib.message_from_bytes(raw_email)
                    reply = self._parse_reply(parsed)
                    if reply:
                        replies.append(reply)

                mail.logout()
                return replies
            except imaplib.IMAP4.error as e:
                logger.error(f"IMAP error: {e}")
                return []
            except Exception as e:
                logger.error(f"Unexpected IMAP error: {e}")
                return []

        return await loop.run_in_executor(None, _poll)

    def _parse_reply(self, parsed_msg) -> Optional[dict]:
        try:
            from_email = parsed_msg.get("From", "")
            subject = parsed_msg.get("Subject", "")
            received_at = parsed_msg.get("Date", "")
            in_reply_to = parsed_msg.get("In-Reply-To", "")
            references = parsed_msg.get("References", "")

            # Extract body
            body = ""
            if parsed_msg.is_multipart():
                for part in parsed_msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        try:
                            body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                            break
                        except Exception:
                            continue
            else:
                try:
                    body = parsed_msg.get_payload(decode=True).decode("utf-8", errors="ignore")
                except Exception:
                    body = str(parsed_msg.get_payload())

            classification = self._classify_reply(body, subject)

            # Parse date
            try:
                dt = parsedate_to_datetime(received_at)
                received_at_iso = dt.isoformat() if dt else None
            except Exception:
                received_at_iso = None

            return {
                "from_email": from_email,
                "subject": subject,
                "body": body[:5000],
                "classification": classification,
                "received_at": received_at_iso,
                "in_reply_to": in_reply_to,
                "references": references,
            }
        except Exception as e:
            logger.error(f"Failed to parse reply: {e}")
            return None

    @staticmethod
    def _classify_reply(body: str, subject: str) -> str:
        text = f"{subject} {body}".lower()

        for kw in OUT_OF_OFFICE_KEYWORDS:
            if kw in text:
                return "out_of_office"

        for kw in NOT_INTERESTED_KEYWORDS:
            if kw in text:
                return "not_interested"

        for kw in INTERESTED_KEYWORDS:
            if kw in text:
                return "interested"

        return "replied"


backlink_outreach_reply_monitor = BacklinkOutreachReplyMonitor()