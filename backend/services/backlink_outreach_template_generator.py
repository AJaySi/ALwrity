"""AI-powered outreach email template generation."""

from __future__ import annotations

import json
import re
from typing import List, Optional
from loguru import logger

from services.llm_providers.main_text_generation import llm_text_gen


SYSTEM_PROMPT = """You are an expert outreach copywriter specializing in guest post and backlink pitch emails.
Write concise, personalized outreach emails that get high response rates.
Follow these rules:
- Be specific about why you're reaching out (mention their content)
- Keep it under 200 words
- Include a clear call to action
- Sound human, not templated
- Never use spammy phrases
- Output ONLY valid JSON with "subject" and "body" keys"""

SUBJECT_LINES_PROMPT = """You are an expert email subject line writer.
Given an outreach email body, generate subject lines that are:
- Intriguing but not clickbait
- Personalized when possible
- Under 60 characters
- Varied in style (question, curiosity, value-prop)
Output ONLY valid JSON with a "subjects" key containing an array of strings."""

FOLLOW_UP_PROMPT = """You are an expert outreach copywriter.
Write a polite follow-up email for a guest post pitch that hasn't received a response.
Rules:
- Reference the original email without repeating it verbatim
- Keep it shorter than the original (under 100 words)
- Add a new angle or piece of value
- Include a clear call to action
- Sound human and respectful, never pushy
- Output ONLY valid JSON with "subject" and "body" keys"""

PERSONALIZATION_PROMPT = """You are an expert outreach personalization specialist.
Given a lead's information and a draft outreach email, personalize it for that specific lead.
Rules:
- Mention their specific content or website
- Reference something relevant from their site
- Keep the core pitch but make it feel custom-written
- Under 200 words
- Output ONLY valid JSON with "subject" and "body" keys"""


def generate_outreach_email(
    topic: str,
    target_site: Optional[str] = None,
    tone: str = "professional",
    user_id: str = "default",
    existing_body: Optional[str] = None,
) -> dict:
    """Generate an outreach email using the LLM.

    Args:
        topic: The topic/keyword to pitch.
        target_site: Optional target website name/URL.
        tone: professional, friendly, casual, or formal.
        user_id: Clerk user ID for subscription check.
        existing_body: If provided, rewrite/improve this existing template.

    Returns:
        dict with "subject" and "body" keys.
    """
    if existing_body:
        prompt = (
            f"Rewrite and improve the following outreach email for a {tone} tone. "
            f"Topic: {topic}. "
            f"{f'Target website: {target_site}. ' if target_site else ''}"
            f"Keep the core message but make it more effective. "
            f"Original email:\n\n{existing_body}\n\n"
            f"Return ONLY valid JSON with 'subject' and 'body' keys."
        )
    else:
        prompt = (
            f"Write a {tone} outreach email for a guest post opportunity about: {topic}. "
            f"{f'We are pitching this to: {target_site}. ' if target_site else ''}"
            f"Mention specific value the guest post would bring to their audience. "
            f"Return ONLY valid JSON with 'subject' and 'body' keys."
        )

    try:
        raw = llm_text_gen(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            user_id=user_id,
            temperature=0.7,
        )

        result = _parse_json_response(raw)
        if result:
            return result

        return _fallback_extract(raw, topic)

    except Exception as e:
        logger.error(f"Failed to generate outreach email: {e}")
        return {
            "subject": f"Guest post opportunity: {topic}",
            "body": f"Hi there,\n\nI came across your site and I'd love to contribute a guest post about {topic}. "
                     f"Please let me know if you're open to submissions.\n\nBest regards",
        }


def generate_personalized_email(
    lead_name: str,
    lead_site: str,
    lead_content_topic: str,
    pitch_topic: str,
    existing_body: str = "",
    user_id: str = "default",
) -> dict:
    """Personalize an outreach email for a specific lead.

    Args:
        lead_name: Contact name or site owner name.
        lead_site: The lead's website URL.
        lead_content_topic: Topic of relevant content on their site.
        pitch_topic: The topic we want to pitch.
        existing_body: Optional draft to personalize further.
        user_id: Clerk user ID for subscription check.

    Returns:
        dict with "subject" and "body" keys.
    """
    if existing_body:
        prompt = (
            f"Personalize this outreach email for {lead_name} from {lead_site}. "
            f"They have content about '{lead_content_topic}'. "
            f"We want to pitch: {pitch_topic}. "
            f"Mention something specific about their content on {lead_content_topic} "
            f"to show we've done our research. "
            f"Draft email to personalize:\n\n{existing_body}\n\n"
            f"Return ONLY valid JSON with 'subject' and 'body' keys."
        )
    else:
        prompt = (
            f"Write a personalized outreach email to {lead_name} at {lead_site}. "
            f"They have published content about '{lead_content_topic}'. "
            f"We want to pitch a guest post about: {pitch_topic}. "
            f"Reference their article on {lead_content_topic} and explain how our pitch "
            f"would provide value to their audience. "
            f"Return ONLY valid JSON with 'subject' and 'body' keys."
        )

    try:
        raw = llm_text_gen(
            prompt=prompt,
            system_prompt=PERSONALIZATION_PROMPT,
            user_id=user_id,
            temperature=0.7,
        )
        result = _parse_json_response(raw)
        if result:
            return result
        return _fallback_extract(raw, pitch_topic)
    except Exception as e:
        logger.error(f"Failed to personalize email: {e}")
        return {"subject": f"Question about your content on {lead_content_topic}", "body": existing_body or f"Hi {lead_name},\n\nI enjoyed your article about {lead_content_topic}..."}


def generate_subject_lines(
    body: str,
    count: int = 5,
    user_id: str = "default",
) -> List[str]:
    """Generate subject line suggestions for an email body.

    Args:
        body: The email body to generate subject lines for.
        count: Number of subject lines to generate.
        user_id: Clerk user ID for subscription check.

    Returns:
        List of subject line strings.
    """
    prompt = (
        f"Generate {count} subject lines for the following outreach email. "
        f"Make them varied in style and optimized for open rates.\n\n"
        f"Email body:\n{body}\n\n"
        f"Return ONLY valid JSON with a 'subjects' key containing an array of strings."
    )

    try:
        raw = llm_text_gen(
            prompt=prompt,
            system_prompt=SUBJECT_LINES_PROMPT,
            user_id=user_id,
            temperature=0.8,
        )
        if raw:
            text = raw.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            try:
                data = json.loads(text)
                if isinstance(data, dict) and "subjects" in data and isinstance(data["subjects"], list):
                    return [s.strip() for s in data["subjects"][:count]]
            except json.JSONDecodeError:
                pass
        lines = [l.strip("- ").strip() for l in raw.strip().split("\n") if l.strip() and not l.strip().startswith("```")]
        return [l for l in lines if len(l) > 10][:count]
    except Exception as e:
        logger.error(f"Failed to generate subject lines: {e}")
        return [f"Guest post opportunity", f"Question about your content", f"Collaboration idea"]


def generate_follow_up(
    original_subject: str,
    original_body: str,
    days_elapsed: int = 7,
    reply_context: str = "",
    user_id: str = "default",
) -> dict:
    """Generate a follow-up email for an outreach that hasn't received a response.

    Args:
        original_subject: Subject line of the original email.
        original_body: Body of the original email.
        days_elapsed: Number of days since the original was sent.
        reply_context: If the recipient replied, context of their reply.
        user_id: Clerk user ID for subscription check.

    Returns:
        dict with "subject" and "body" keys.
    """
    if reply_context:
        prompt = (
            f"The recipient replied with: '{reply_context}'. "
            f"Write a follow-up email that addresses their response and keeps the conversation moving. "
            f"Original subject: {original_subject}.\n\n"
            f"Original email:\n{original_body}\n\n"
            f"Return ONLY valid JSON with 'subject' and 'body' keys."
        )
    else:
        prompt = (
            f"Write a polite follow-up email. {days_elapsed} days have passed since the original email. "
            f"Do not apologize for following up. Add a new piece of value or angle. "
            f"Original subject: {original_subject}.\n\n"
            f"Original email:\n{original_body}\n\n"
            f"Return ONLY valid JSON with 'subject' and 'body' keys."
        )

    try:
        raw = llm_text_gen(
            prompt=prompt,
            system_prompt=FOLLOW_UP_PROMPT,
            user_id=user_id,
            temperature=0.7,
        )
        result = _parse_json_response(raw)
        if result:
            return result
        return _fallback_extract(raw, original_subject)
    except Exception as e:
        logger.error(f"Failed to generate follow-up: {e}")
        return {
            "subject": f"Re: {original_subject}",
            "body": f"Hi there,\n\nI wanted to follow up on my previous email. "
                    f"I'd love to hear your thoughts when you have a moment.\n\nBest regards",
        }


def _parse_json_response(raw: str) -> Optional[dict]:
    """Try to parse JSON from LLM response, handling markdown fences."""
    if not raw:
        return None

    text = raw.strip()

    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

    try:
        data = json.loads(text)
        if isinstance(data, dict) and "subject" in data and "body" in data:
            return {"subject": data["subject"].strip(), "body": data["body"].strip()}
    except json.JSONDecodeError:
        pass

    return None


def _fallback_extract(raw: str, topic: str) -> dict:
    """Fallback: try to extract subject line and body from unstructured text."""
    lines = [l.strip() for l in raw.strip().split("\n") if l.strip()]
    subject = topic
    body_lines = []

    for i, line in enumerate(lines):
        lower = line.lower()
        if lower.startswith("subject") or lower.startswith("subject:"):
            subject = line.split(":", 1)[-1].strip()
        elif lower.startswith("body") or lower.startswith("body:"):
            body_lines.append(line.split(":", 1)[-1].strip())
        else:
            body_lines.append(line)

    body = "\n".join(body_lines) if body_lines else raw
    return {"subject": subject, "body": body}