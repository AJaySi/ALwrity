"""
Email Extraction Service for Backlinking Opportunities

Extracts and validates email addresses from scraped web content to create
fully qualified leads for outreach campaigns.

Key Features:
- Regex-based email extraction from HTML/text content
- Contact page discovery and scraping
- Email validation and deduplication
- Privacy compliance filtering
- Multiple extraction strategies
- Confidence scoring for email quality
"""

import re
import asyncio
from typing import List, Dict, Optional, Any, Set, Tuple
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
import aiohttp
from bs4 import BeautifulSoup
from loguru import logger

from .logging_utils import campaign_logger


class EmailExtractionService:
    """
    Service for extracting email addresses from web content.

    Provides comprehensive email discovery including:
    - Direct extraction from provided content
    - Contact page discovery and scraping
    - Email validation and quality assessment
    - Privacy and compliance filtering
    """

    def __init__(self, max_contact_pages: int = 3, request_timeout: int = 10):
        """
        Initialize the email extraction service.

        Args:
            max_contact_pages: Maximum contact pages to check per domain
            request_timeout: Timeout for HTTP requests in seconds
        """
        self.max_contact_pages = max_contact_pages
        self.request_timeout = request_timeout

        # Email validation patterns
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            re.IGNORECASE
        )

        # Common contact page patterns
        self.contact_page_patterns = [
            r'/contact/?$',
            r'/contact-us/?$',
            r'/get-in-touch/?$',
            r'/reach-us/?$',
            r'/about/?$',
            r'/about-us/?$',
            r'/team/?$',
            r'/staff/?$',
            r'/write-for-us/?$',
            r'/guest-post/?$',
            r'/contribute/?$',
            r'/submit/?$',
            r'/guest-blogging/?$',
            r'/become-a-contributor/?$'
        ]

        # Privacy and compliance filters
        self.privacy_filters = {
            'personal_domains': [
                'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
                'aol.com', 'icloud.com', 'protonmail.com', 'zoho.com'
            ],
            'spam_indicators': [
                'spam', 'junk', 'test', 'example', 'noreply', 'no-reply',
                'donotreply', 'admin', 'webmaster', 'root', 'postmaster'
            ],
            'temporary_domains': [
                '10minutemail.com', 'temp-mail.org', 'guerrillamail.com',
                'mailinator.com', 'throwaway.email'
            ]
        }

        # Rate limiting
        self.request_semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests

        campaign_logger.info("EmailExtractionService initialized")

    async def extract_emails_from_opportunity(
        self,
        url: str,
        content: str,
        title: str = "",
        base_url: str = None
    ) -> Dict[str, Any]:
        """
        Extract emails from a backlinking opportunity.

        Args:
            url: Opportunity URL
            content: Scraped content from the URL
            title: Page title
            base_url: Base URL for relative link resolution

        Returns:
            Dictionary with extracted emails and metadata
        """
        try:
            campaign_logger.debug(f"Extracting emails from: {url}")

            # Extract emails from provided content
            direct_emails = self._extract_emails_from_content(content)

            # If we found emails in the main content, that's great
            if direct_emails:
                campaign_logger.debug(f"Found {len(direct_emails)} emails in main content")
                validated_emails = await self._validate_and_filter_emails(direct_emails, url)
                return self._format_extraction_result(validated_emails, "direct", url)

            # If no emails found, try to find contact pages
            campaign_logger.debug("No emails in main content, checking contact pages")
            contact_emails = await self._extract_from_contact_pages(url, base_url)

            if contact_emails:
                campaign_logger.debug(f"Found {len(contact_emails)} emails in contact pages")
                validated_emails = await self._validate_and_filter_emails(contact_emails, url)
                return self._format_extraction_result(validated_emails, "contact_page", url)

            # If still no emails, try alternative extraction methods
            campaign_logger.debug("No emails found, trying alternative methods")
            alternative_emails = await self._extract_emails_alternatively(url, content)

            if alternative_emails:
                campaign_logger.debug(f"Found {len(alternative_emails)} emails via alternative methods")
                validated_emails = await self._validate_and_filter_emails(alternative_emails, url)
                return self._format_extraction_result(validated_emails, "alternative", url)

            # No emails found
            campaign_logger.debug(f"No emails found for: {url}")
            return self._format_extraction_result([], "none_found", url)

        except Exception as e:
            campaign_logger.error(f"Error extracting emails from {url}: {e}")
            return self._format_extraction_result([], "error", url, error=str(e))

    def _extract_emails_from_content(self, content: str) -> List[str]:
        """
        Extract email addresses from text content using regex.

        Args:
            content: Text content to search

        Returns:
            List of found email addresses
        """
        if not content:
            return []

        # Find all email matches
        matches = self.email_pattern.findall(content)

        # Clean and deduplicate
        emails = []
        seen = set()

        for email in matches:
            email = email.strip().lower()
            if email not in seen and len(email) <= 254:  # RFC 5321 limit
                emails.append(email)
                seen.add(email)

        return emails

    async def _extract_from_contact_pages(
        self,
        url: str,
        base_url: Optional[str] = None
    ) -> List[str]:
        """
        Discover and scrape contact pages for email addresses.

        Args:
            url: Original opportunity URL
            base_url: Base URL for the domain

        Returns:
            List of email addresses found in contact pages
        """
        try:
            # Determine base URL
            if not base_url:
                parsed = urlparse(url)
                base_url = f"{parsed.scheme}://{parsed.netloc}"

            # Generate potential contact page URLs
            contact_urls = self._generate_contact_page_urls(base_url)

            # Scrape contact pages concurrently
            emails_found = []
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.request_timeout)
            ) as session:

                tasks = []
                for contact_url in contact_urls[:self.max_contact_pages]:
                    tasks.append(self._scrape_contact_page(session, contact_url))

                # Execute concurrently with semaphore
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for result in results:
                    if isinstance(result, list):
                        emails_found.extend(result)
                    elif isinstance(result, Exception):
                        campaign_logger.debug(f"Contact page scraping error: {result}")

            # Deduplicate
            return list(set(emails_found))

        except Exception as e:
            campaign_logger.warning(f"Error extracting from contact pages: {e}")
            return []

    def _generate_contact_page_urls(self, base_url: str) -> List[str]:
        """
        Generate potential contact page URLs for a domain.

        Args:
            base_url: Base URL of the domain

        Returns:
            List of potential contact page URLs
        """
        urls = []

        # Clean base URL
        base_url = base_url.rstrip('/')

        # Common contact page paths
        contact_paths = [
            '/contact',
            '/contact-us',
            '/contact.html',
            '/get-in-touch',
            '/reach-us',
            '/about',
            '/about-us',
            '/about.html',
            '/team',
            '/staff',
            '/write-for-us',
            '/guest-post',
            '/contribute',
            '/submit',
            '/guest-blogging',
            '/become-a-contributor'
        ]

        for path in contact_paths:
            urls.append(f"{base_url}{path}")
            urls.append(f"{base_url}{path}.html")
            urls.append(f"{base_url}{path}.php")

        return urls

    async def _scrape_contact_page(self, session: aiohttp.ClientSession, url: str) -> List[str]:
        """
        Scrape a single contact page for email addresses.

        Args:
            session: HTTP session
            url: URL to scrape

        Returns:
            List of email addresses found
        """
        async with self.request_semaphore:
            try:
                campaign_logger.debug(f"Scraping contact page: {url}")

                async with session.get(
                    url,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    },
                    allow_redirects=True
                ) as response:

                    if response.status != 200:
                        return []

                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    # Remove script and style elements
                    for script in soup(["script", "style"]):
                        script.decompose()

                    # Extract text content
                    text = soup.get_text()

                    # Extract emails
                    emails = self._extract_emails_from_content(text)

                    # Also check for mailto links
                    mailto_emails = self._extract_emails_from_mailto_links(soup)
                    emails.extend(mailto_emails)

                    return list(set(emails))

            except Exception as e:
                campaign_logger.debug(f"Error scraping {url}: {e}")
                return []

    def _extract_emails_from_mailto_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract emails from mailto links in HTML.

        Args:
            soup: BeautifulSoup object

        Returns:
            List of email addresses from mailto links
        """
        emails = []

        # Find all mailto links
        mailto_links = soup.find_all('a', href=re.compile(r'^mailto:', re.IGNORECASE))

        for link in mailto_links:
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href[7:].split('?')[0].strip().lower()  # Remove query params
                if self.email_pattern.match(email):
                    emails.append(email)

        return list(set(emails))

    async def _extract_emails_alternatively(self, url: str, content: str) -> List[str]:
        """
        Try alternative email extraction methods.

        Args:
            url: Opportunity URL
            content: Original content

        Returns:
            List of emails found via alternative methods
        """
        emails = []

        try:
            # Try to find email patterns in JavaScript code
            js_emails = self._extract_emails_from_javascript(content)
            emails.extend(js_emails)

            # Try to find emails in JSON-LD structured data
            json_emails = self._extract_emails_from_json_ld(content)
            emails.extend(json_emails)

            # Try to find emails in meta tags
            meta_emails = self._extract_emails_from_meta_tags(content)
            emails.extend(meta_emails)

        except Exception as e:
            campaign_logger.debug(f"Alternative extraction error: {e}")

        return list(set(emails))

    def _extract_emails_from_javascript(self, content: str) -> List[str]:
        """Extract emails from JavaScript code in HTML."""
        emails = []

        # Find JavaScript code blocks
        js_pattern = re.compile(r'<script[^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
        js_blocks = js_pattern.findall(content)

        for js_block in js_blocks:
            js_emails = self._extract_emails_from_content(js_block)
            emails.extend(js_emails)

        return list(set(emails))

    def _extract_emails_from_json_ld(self, content: str) -> List[str]:
        """Extract emails from JSON-LD structured data."""
        emails = []

        try:
            # Find JSON-LD scripts
            json_ld_pattern = re.compile(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)
            json_scripts = json_ld_pattern.findall(content)

            for script in json_scripts:
                try:
                    import json
                    data = json.loads(script.strip())

                    # Recursively search for emails in JSON data
                    def find_emails(obj):
                        if isinstance(obj, dict):
                            for key, value in obj.items():
                                if 'email' in key.lower():
                                    if isinstance(value, str) and self.email_pattern.match(value):
                                        emails.append(value.lower())
                                else:
                                    find_emails(value)
                        elif isinstance(obj, list):
                            for item in obj:
                                find_emails(item)

                    find_emails(data)

                except (json.JSONDecodeError, TypeError):
                    continue

        except Exception as e:
            campaign_logger.debug(f"JSON-LD extraction error: {e}")

        return list(set(emails))

    def _extract_emails_from_meta_tags(self, content: str) -> List[str]:
        """Extract emails from meta tags."""
        emails = []

        try:
            soup = BeautifulSoup(content, 'html.parser')

            # Look for meta tags that might contain contact info
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                content_attr = meta.get('content', '')
                if content_attr:
                    meta_emails = self._extract_emails_from_content(content_attr)
                    emails.extend(meta_emails)

        except Exception as e:
            campaign_logger.debug(f"Meta tag extraction error: {e}")

        return list(set(emails))

    async def _validate_and_filter_emails(self, emails: List[str], source_url: str) -> List[Dict[str, Any]]:
        """
        Validate and filter email addresses for quality and compliance.

        Args:
            emails: List of email addresses to validate
            source_url: Source URL for context

        Returns:
            List of validated email dictionaries
        """
        validated_emails = []

        for email in emails:
            try:
                # Basic validation
                if not self._is_valid_email_format(email):
                    continue

                # Privacy and compliance filtering
                if not self._passes_privacy_filters(email):
                    continue

                # Quality scoring
                quality_score = self._calculate_email_quality_score(email, source_url)

                # Only include high-quality emails
                if quality_score >= 0.6:
                    validated_emails.append({
                        'email': email,
                        'quality_score': quality_score,
                        'validation_status': 'valid',
                        'source_type': 'extracted',
                        'confidence_level': self._determine_confidence_level(quality_score)
                    })

            except Exception as e:
                campaign_logger.debug(f"Email validation error for {email}: {e}")
                continue

        # Sort by quality score
        validated_emails.sort(key=lambda x: x['quality_score'], reverse=True)

        return validated_emails

    def _is_valid_email_format(self, email: str) -> bool:
        """
        Validate basic email format.

        Args:
            email: Email address to validate

        Returns:
            True if format is valid
        """
        if not email or len(email) > 254:
            return False

        # Use regex pattern
        return bool(self.email_pattern.match(email))

    def _passes_privacy_filters(self, email: str) -> bool:
        """
        Check if email passes privacy and compliance filters.

        Args:
            email: Email address to check

        Returns:
            True if email passes all filters
        """
        domain = email.split('@')[-1].lower()

        # Check against personal email domains
        if domain in self.privacy_filters['personal_domains']:
            return False

        # Check against temporary/throwaway domains
        if domain in self.privacy_filters['temporary_domains']:
            return False

        # Check for spam indicators in local part
        local_part = email.split('@')[0].lower()
        if any(indicator in local_part for indicator in self.privacy_filters['spam_indicators']):
            return False

        return True

    def _calculate_email_quality_score(self, email: str, source_url: str) -> float:
        """
        Calculate quality score for an email address.

        Args:
            email: Email address
            source_url: Source URL

        Returns:
            Quality score between 0-1
        """
        score = 0.5  # Base score

        domain = email.split('@')[-1].lower()
        local_part = email.split('@')[0].lower()

        # Domain authority indicators
        if any(tld in domain for tld in ['.edu', '.gov', '.org', '.ac.uk']):
            score += 0.2

        # Professional email patterns
        professional_patterns = ['contact', 'info', 'admin', 'editor', 'press', 'media']
        if any(pattern in local_part for pattern in professional_patterns):
            score += 0.15

        # Length appropriateness
        if 5 <= len(local_part) <= 20:
            score += 0.1

        # Avoid obviously generic emails
        generic_patterns = ['test', 'example', 'user', 'admin123']
        if any(pattern in local_part for pattern in generic_patterns):
            score -= 0.2

        # Domain matches source URL (good sign)
        source_domain = urlparse(source_url).netloc.lower()
        if domain in source_domain or source_domain in domain:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _determine_confidence_level(self, quality_score: float) -> str:
        """
        Determine confidence level based on quality score.

        Args:
            quality_score: Quality score

        Returns:
            Confidence level string
        """
        if quality_score >= 0.8:
            return "high"
        elif quality_score >= 0.7:
            return "medium"
        else:
            return "low"

    def _format_extraction_result(
        self,
        emails: List[Dict[str, Any]],
        method: str,
        source_url: str,
        error: str = None
    ) -> Dict[str, Any]:
        """
        Format the extraction result.

        Args:
            emails: List of validated emails
            method: Extraction method used
            source_url: Source URL
            error: Error message if any

        Returns:
            Formatted result dictionary
        """
        return {
            'emails': emails,
            'email_count': len(emails),
            'extraction_method': method,
            'source_url': source_url,
            'has_emails': len(emails) > 0,
            'best_email': emails[0]['email'] if emails else None,
            'best_email_quality': emails[0]['quality_score'] if emails else 0,
            'error': error,
            'extraction_timestamp': datetime.utcnow().isoformat()
        }

    # ===== BATCH PROCESSING METHODS =====

    async def extract_emails_batch(
        self,
        opportunities: List[Dict[str, Any]],
        batch_size: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Extract emails from multiple opportunities in batches.

        Args:
            opportunities: List of opportunity dictionaries
            batch_size: Number of concurrent extractions

        Returns:
            List of opportunities with email extraction results
        """
        semaphore = asyncio.Semaphore(batch_size)
        results = []

        async def process_opportunity(opp: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                try:
                    url = opp.get('url', '')
                    content = opp.get('content', '')
                    title = opp.get('title', '')

                    # Extract emails
                    email_result = await self.extract_emails_from_opportunity(
                        url=url,
                        content=content,
                        title=title
                    )

                    # Add email data to opportunity
                    opp_copy = opp.copy()
                    opp_copy['email_extraction'] = email_result

                    return opp_copy

                except Exception as e:
                    campaign_logger.error(f"Batch email extraction error for {opp.get('url')}: {e}")
                    opp_copy = opp.copy()
                    opp_copy['email_extraction'] = {
                        'emails': [],
                        'email_count': 0,
                        'extraction_method': 'error',
                        'error': str(e)
                    }
                    return opp_copy

        # Process all opportunities
        tasks = [process_opportunity(opp) for opp in opportunities]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out exceptions
        valid_results = [r for r in results if not isinstance(r, Exception)]

        campaign_logger.info(f"Batch email extraction completed: {len(valid_results)}/{len(opportunities)} opportunities processed")

        return valid_results