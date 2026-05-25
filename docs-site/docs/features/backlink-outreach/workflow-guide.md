# Backlink Outreach Workflow Guide

This guide walks through the complete Backlink Outreach lifecycle from campaign creation to analytics review.

## 1) Create a Campaign

Campaigns group your leads, outreach attempts, replies, and analytics together. Every action in the system belongs to a campaign.

!!! tip "Best practice"
    Create one campaign per target vertical or client. For example: "SaaS Growth Blogs Q3" or "Fitness Influencer Outreach".

**What to validate before continuing:**
- Campaign name is descriptive enough to distinguish from others.
- You have a clear keyword or niche for discovery.

## 2) Discover Opportunities

Use AI-powered discovery to find websites that accept guest posts in your niche.

!!! note "How discovery works"
    The system combines **Exa neural search** (semantic understanding) with **DuckDuckGo** (broad coverage), scrapes full pages, extracts contact emails, and scores each opportunity for quality and guest-post likelihood.

**Recommended sequence:**
1. Enter a keyword (e.g., "AI marketing", "SaaS growth").
2. Click **Discover** to search across multiple query patterns ("write for us", "guest contributor", etc.).
3. Review results — check quality score, confidence score, and email detection badges.
4. Select a campaign and click **Save to Campaign** to persist leads.

**What to look for:**
- Quality score > 60% — the site is relevant to your keyword.
- Confidence score > 50% — the site likely accepts guest posts.
- "Has guidelines" badge — the site has a dedicated guest post page.
- "Email found" badge — a contact email was extracted.

## 3) Compose Outreach Emails

Use the AI email composer to craft personalized outreach messages.

!!! note "AI generation options"
    - **Generate**: Create an email from a topic, tone, and optional template.
    - **Personalize**: Tailor an email to a specific lead (name, site, content topic).
    - **Subject Lines**: Get 5-10 AI-suggested subject line variants.
    - **Follow-up**: Generate a polite follow-up referencing the original email.

**Recommended sequence:**
1. Choose a template or start fresh.
2. Enter your topic and target site (optional).
3. Select a tone (Professional, Friendly, Casual, Formal).
4. Click **Generate with AI** to create a subject + body.
5. Optionally click **Suggest** for subject line variants.
6. Use **Personalize** to tailor the email to a specific lead.
7. Preview the email in the live preview pane.

## 4) Send Outreach

Once your email is composed, navigate to the Leads tab to send outreach.

!!! warning "Policy validation"
    Every send is validated against your daily caps, suppression list, and GDPR rules. EU-domain leads automatically use "consent" as legal basis; others use "legitimate_interest".

**What happens when you send:**
1. Policy is validated (caps, suppression, idempotency, legal basis).
2. An outreach attempt is recorded in the database.
3. If approved, the email is sent via SMTP with TLS.
4. Send counters are incremented **only after successful delivery**.
5. Idempotency key is marked to prevent duplicate sends.
6. Lead status is updated to "contacted".

**Daily limits:**
- 100 emails per user per day.
- 20 emails per domain per day.

## 5) Monitor Replies

After sending outreach, monitor replies through the IMAP-powered inbox.

!!! note "Auto-classification"
    Replies are automatically classified as:
    - **Interested** — positive language detected ("sounds good", "tell me more").
    - **Not interested** — negative language ("not interested", "unsubscribe").
    - **Out of office** — auto-responder detected.
    - **Replied** — general reply without strong signals.

**What to do with classified replies:**
- **Interested**: Move the lead to "replied" status, then "placed" after publication.
- **Not interested**: Mark as "bounced" or leave as-is. The sender is auto-added to suppression.
- **Out of office**: Schedule a follow-up for after their return date.
- **Replied**: Read and manually classify, then update lead status.

## 6) Track Analytics

Monitor campaign performance with built-in analytics.

**Key metrics:**
- **Send Volume**: Daily email send trend over time.
- **Response Rate**: Percentage of sent emails that received a reply.
- **Placement Rate**: Percentage of leads that resulted in a published post.
- **Conversion Funnel**: Lead count by status stage (discovered → contacted → replied → placed).
- **Reply Classification**: Breakdown of reply types.

**Export options:**
- Export Leads as CSV for CRM import.
- Export Attempts for audit trails.
- Export Replies for analysis in spreadsheets.

!!! tip "CSV safety"
    All CSV exports are sanitized against formula injection — cells starting with `=`, `+`, `-`, or `@` are automatically escaped.

## 7) Iterate and Optimize

Use analytics insights to improve your outreach:

1. **Low response rate?** Try different subject lines or tones.
2. **High bounce rate?** Improve lead quality filters during discovery.
3. **Low placement rate?** Refine your pitch personalization.
4. **Many "not interested"?** Adjust your target niche or messaging.

---

*Now you know the full workflow! Dive deeper with [Campaign Management](campaign-management.md) or [Discovery](discovery.md).*
