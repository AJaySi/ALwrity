"""
Email Automation Service for Backlinking

Handles email sending, tracking, and response monitoring for backlinking campaigns.
Supports SMTP for sending emails and IMAP for checking responses.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import asyncio
import smtplib
import imaplib
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import decode_header
import re
from loguru import logger


@dataclass
class EmailRecord:
    """Represents an email record in the system."""
    id: int
    campaign_id: str
    opportunity_url: str
    recipient_email: str
    subject: str
    body: str
    status: str = "draft"  # draft, sent, delivered, bounced, replied
    sent_at: Optional[datetime] = None
    replied_at: Optional[datetime] = None
    follow_up_count: int = 0


@dataclass
class EmailResponse:
    """Represents an email response."""
    from_email: str
    subject: str
    body: str
    received_at: datetime
    is_positive: bool = False
    needs_follow_up: bool = False


class EmailAutomationService:
    """
    Service for automating email operations in backlinking campaigns.

    Handles sending personalized emails, tracking delivery, and monitoring responses.
    """

    def __init__(self):
        self.smtp_timeout = 30
        self.imap_timeout = 30
        self.max_follow_ups = 3

    async def send_bulk_emails(
        self,
        email_records: List[Dict[str, Any]],
        smtp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send multiple emails using SMTP configuration.

        Args:
            email_records: List of email records to send
            smtp_config: SMTP server configuration

        Returns:
            Results summary with sent/failed counts
        """
        try:
            sent_count = 0
            failed_count = 0
            results = []

            for email_record in email_records:
                try:
                    success = await self._send_single_email(
                        email_record=email_record,
                        smtp_config=smtp_config
                    )

                    if success:
                        sent_count += 1
                        results.append({
                            "email_record": email_record,
                            "status": "sent",
                            "sent_at": datetime.now()
                        })
                    else:
                        failed_count += 1
                        results.append({
                            "email_record": email_record,
                            "status": "failed"
                        })

                except Exception as e:
                    logger.error(f"Failed to send email to {email_record.get('recipient_email')}: {e}")
                    failed_count += 1
                    results.append({
                        "email_record": email_record,
                        "status": "error",
                        "error": str(e)
                    })

            logger.info(f"Email sending completed: {sent_count} sent, {failed_count} failed")
            return {
                "sent": sent_count,
                "failed": failed_count,
                "total": len(email_records),
                "results": results
            }

        except Exception as e:
            logger.error(f"Failed to send bulk emails: {e}")
            raise

    async def _send_single_email(
        self,
        email_record: Dict[str, Any],
        smtp_config: Dict[str, Any]
    ) -> bool:
        """
        Send a single email using SMTP.

        Args:
            email_record: Email record to send
            smtp_config: SMTP configuration

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_config['user']
            msg['To'] = email_record['recipient_email']
            msg['Subject'] = email_record['subject']

            # Add body
            msg.attach(MIMEText(email_record['body'], 'plain'))

            # Send email
            server = smtplib.SMTP(
                smtp_config['server'],
                smtp_config['port']
            )
            server.starttls()
            server.login(smtp_config['user'], smtp_config['password'])
            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent successfully to {email_record['recipient_email']}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {email_record['recipient_email']}: {e}")
            return False

    async def check_responses(self, imap_config: Dict[str, Any]) -> List[EmailResponse]:
        """
        Check for email responses using IMAP.

        Args:
            imap_config: IMAP server configuration

        Returns:
            List of email responses
        """
        try:
            responses = []

            # Connect to IMAP server
            mail = imaplib.IMAP4_SSL(imap_config['server'])
            mail.login(imap_config['user'], imap_config['password'])
            mail.select('inbox')

            # Search for unread messages
            status, messages = mail.search(None, 'UNSEEN')

            if status != 'OK':
                logger.error("Failed to search for unread messages")
                return responses

            message_ids = messages[0].split()

            for msg_id in message_ids:
                try:
                    # Fetch message
                    status, msg_data = mail.fetch(msg_id, '(RFC822)')

                    if status != 'OK':
                        continue

                    email_message = email.message_from_bytes(msg_data[0][1])

                    # Parse response
                    response = self._parse_email_response(email_message)

                    if response:
                        responses.append(response)

                except Exception as e:
                    logger.error(f"Failed to process message {msg_id}: {e}")
                    continue

            mail.logout()

            logger.info(f"Found {len(responses)} email responses")
            return responses

        except Exception as e:
            logger.error(f"Failed to check email responses: {e}")
            raise

    def _parse_email_response(self, email_message) -> Optional[EmailResponse]:
        """
        Parse an email message into an EmailResponse object.

        Args:
            email_message: Email message object

        Returns:
            EmailResponse object or None if parsing failed
        """
        try:
            # Extract sender
            from_header = email_message['From']
            from_email = self._extract_email_from_header(from_header)

            if not from_email:
                return None

            # Extract subject
            subject = email_message['Subject'] or ""
            subject = self._decode_header(subject)

            # Extract date
            date_str = email_message['Date']
            received_at = self._parse_email_date(date_str)

            # Extract body
            body = self._extract_email_body(email_message)

            # Analyze response
            analysis = self._analyze_response_content(subject, body)

            return EmailResponse(
                from_email=from_email,
                subject=subject,
                body=body,
                received_at=received_at,
                is_positive=analysis.get('is_positive', False),
                needs_follow_up=analysis.get('needs_follow_up', False)
            )

        except Exception as e:
            logger.error(f"Failed to parse email response: {e}")
            return None

    async def send_follow_up_emails(
        self,
        follow_up_candidates: List[Dict[str, Any]],
        smtp_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Send follow-up emails for non-responsive contacts.

        Args:
            follow_up_candidates: List of opportunities needing follow-up
            smtp_config: SMTP configuration

        Returns:
            Follow-up sending results
        """
        try:
            sent_count = 0
            results = []

            for candidate in follow_up_candidates:
                if candidate.get('follow_up_count', 0) >= self.max_follow_ups:
                    continue

                try:
                    follow_up_email = self._generate_follow_up_email(candidate)

                    success = await self._send_single_email(
                        email_record={
                            'recipient_email': candidate['contact_email'],
                            'subject': follow_up_email['subject'],
                            'body': follow_up_email['body']
                        },
                        smtp_config=smtp_config
                    )

                    if success:
                        sent_count += 1
                        results.append({
                            "candidate": candidate,
                            "status": "follow_up_sent",
                            "follow_up_number": candidate.get('follow_up_count', 0) + 1
                        })

                except Exception as e:
                    logger.error(f"Failed to send follow-up to {candidate.get('contact_email')}: {e}")
                    results.append({
                        "candidate": candidate,
                        "status": "follow_up_failed",
                        "error": str(e)
                    })

            logger.info(f"Sent {sent_count} follow-up emails")
            return {
                "sent": sent_count,
                "total_candidates": len(follow_up_candidates),
                "results": results
            }

        except Exception as e:
            logger.error(f"Failed to send follow-up emails: {e}")
            raise

    def _generate_follow_up_email(self, candidate: Dict[str, Any]) -> Dict[str, str]:
        """Generate a follow-up email for a candidate."""
        follow_up_number = candidate.get('follow_up_count', 0) + 1

        subject = f"Following up on Guest Post Opportunity - {candidate.get('title', 'Your Site')}"

        body = f"""Subject: {subject}

Dear {candidate.get('contact_name', 'Webmaster')},

I hope this email finds you well. I'm following up on my previous message about contributing a guest post to {candidate.get('title', 'your site')}.

I understand you might be busy, but I'd still love the opportunity to contribute high-quality content on {candidate.get('proposed_topic', 'relevant topics')} to your audience.

Would you be open to discussing this further? I'm happy to adjust the topic or angle based on your preferences.

Looking forward to hearing from you.

Best regards,
{candidate.get('user_name', 'Your Name')}
{candidate.get('user_email', 'your_email@example.com')}
"""

        return {
            "subject": subject,
            "body": body
        }

    def _extract_email_from_header(self, from_header: str) -> Optional[str]:
        """Extract email address from From header."""
        if not from_header:
            return None

        # Simple email extraction using regex
        email_pattern = r'<([^>]+)>|([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        match = re.search(email_pattern, from_header)

        if match:
            return match.group(1) or match.group(2)

        return None

    def _decode_header(self, header: str) -> str:
        """Decode email header if encoded."""
        try:
            decoded_parts = decode_header(header)
            decoded_string = ""

            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8')
                else:
                    decoded_string += str(part)

            return decoded_string
        except:
            return header

    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string."""
        try:
            # Use email.utils.parsedate_to_datetime if available (Python 3.3+)
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except:
            # Fallback to current time
            return datetime.now()

    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email message."""
        try:
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        return part.get_payload(decode=True).decode('utf-8', errors='ignore')
            else:
                return email_message.get_payload(decode=True).decode('utf-8', errors='ignore')

            return ""
        except Exception as e:
            logger.error(f"Failed to extract email body: {e}")
            return ""

    def _analyze_response_content(self, subject: str, body: str) -> Dict[str, bool]:
        """Analyze email response content to determine sentiment and action needed."""
        subject_lower = subject.lower()
        body_lower = body.lower()

        # Check for positive indicators
        positive_keywords = ['yes', 'sure', 'interested', 'great', 'welcome', 'accepted', 'approved']
        is_positive = any(keyword in body_lower for keyword in positive_keywords)

        # Check if follow-up is needed
        follow_up_keywords = ['busy', 'later', 'review', 'consider', 'think about']
        needs_follow_up = any(keyword in body_lower for keyword in follow_up_keywords)

        return {
            'is_positive': is_positive,
            'needs_follow_up': needs_follow_up
        }