# Configuration

Environment variables and deployment configuration for the Backlink Outreach feature.

## SMTP Configuration

Required for sending outreach emails.

| Variable | Required | Default | Description |
|---|---|---|---|
| `SMTP_HOST` | Yes | — | SMTP server hostname. |
| `SMTP_PORT` | No | `587` | SMTP server port. Use 587 for STARTTLS, 465 for implicit TLS. |
| `SMTP_USER` | Yes | — | SMTP authentication username. |
| `SMTP_PASS` | Yes | — | SMTP authentication password. |
| `SMTP_FROM_EMAIL` | Yes | — | Default "From" email address for outreach. |
| `SMTP_FROM_NAME` | No | — | Display name for the From address. |
| `SMTP_VERIFY_TLS` | No | `true` | Verify TLS certificate on SMTP connection. Set to `false` only for local dev. |
| `SMTP_SEND_TIMEOUT` | No | `30` | Timeout in seconds for each SMTP send operation. |

!!! warning "SMTP_VERIFY_TLS"
    Never set `SMTP_VERIFY_TLS=false` in production. Disabling TLS verification exposes you to man-in-the-middle attacks. Only use `false` for local development with self-signed certificates.

## IMAP Configuration

Required for reply monitoring.

| Variable | Required | Default | Description |
|---|---|---|---|
| `IMAP_HOST` | Yes | — | IMAP server hostname. |
| `IMAP_PORT` | No | `993` | IMAP server port. 993 for SSL, 143 for STARTTLS. |
| `IMAP_USER` | Yes | — | IMAP authentication username. |
| `IMAP_PASS` | Yes | — | IMAP authentication password. |
| `IMAP_FETCH_LIMIT` | No | `50` | Maximum messages to process per poll cycle. |

## Search API Configuration

Required for AI-powered opportunity discovery.

| Variable | Required | Default | Description |
|---|---|---|---|
| `EXA_API_KEY` | No | — | Exa neural search API key. Discovery falls back to DuckDuckGo if not set. |

## AI Configuration

Required for email generation and personalization.

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | Yes | — | OpenAI API key for email generation, personalization, and subject suggestions. |

## Policy Configuration

These are currently hardcoded but can be made configurable:

| Setting | Current Value | Description |
|---|---|---|
| Daily user cap | 100 | Max emails per user per day. |
| Daily domain cap | 20 | Max emails per target domain per day. |
| Idempotency window | 24 hours | Duplicate send prevention window. |

## Database Configuration

The Backlink Outreach feature uses SQLite with automatic table creation:

| Variable | Required | Default | Description |
|---|---|---|---|
| `DATABASE_URL` | No | `sqlite+aiosqlite:///./backlink_outreach.db` | Database connection string. |

Tables are created automatically on first use via `_ensure_tables()`. No manual migration is required.

## Deployment Checklist

### Minimal Setup

1. Set all **SMTP** environment variables.
2. Set all **IMAP** environment variables.
3. Set `OPENAI_API_KEY`.
4. Optionally set `EXA_API_KEY` for Exa-powered discovery.
5. Start the backend server.
6. Verify health: `GET /api/v1/backlink-outreach/campaigns` (returns empty list if auth works).

### Production Setup

1. All minimal setup steps.
2. Ensure `SMTP_VERIFY_TLS=true` (default).
3. Set `SMTP_SEND_TIMEOUT` to 30+ seconds for reliable delivery.
4. Set `IMAP_FETCH_LIMIT` based on mailbox volume (50-200).
5. Set up a scheduled job to poll replies every 5-15 minutes.
6. Configure monitoring for SMTP/IMAP connection failures.
7. Review the suppression list periodically.

### Email Provider Setup

The system works with any SMTP/IMAP provider:

| Provider | SMTP Host | SMTP Port | IMAP Host | IMAP Port |
|---|---|---|---|---|
| Gmail | smtp.gmail.com | 587 | imap.gmail.com | 993 |
| Outlook | smtp.office365.com | 587 | outlook.office365.com | 993 |
| SendGrid | smtp.sendgrid.net | 587 | — (use webhooks) | — |
| Mailgun | smtp.mailgun.org | 587 | — (use webhooks) | — |
| Amazon SES | email-smtp.*.amazonaws.com | 587 | — (use SNS) | — |

!!! note "Transaction email providers"
    SendGrid, Mailgun, and Amazon SES don't support IMAP. For reply monitoring with these providers, you'll need to set up inbound webhooks or use a separate IMAP-capable mailbox.

## Security Considerations

| Area | Recommendation |
|---|---|
| **SMTP credentials** | Store in environment variables, never in code or config files. |
| **IMAP credentials** | Use app-specific passwords (Gmail) or dedicated mailbox accounts. |
| **TLS verification** | Always enabled in production (`SMTP_VERIFY_TLS=true`). |
| **Error responses** | 500 errors return generic messages — no stack traces leaked. |
| **Auth** | All endpoints require Clerk authentication. User identity derived from session, not request body. |
| **SQL injection** | Column names are whitelisted and quoted in dynamic SQL. |
| **IMAP injection** | Search terms are sanitized before IMAP SEARCH commands. |
| **CSV injection** | All CSV exports sanitize formula injection characters. |

---

*Next: [Implementation Overview](implementation-overview.md) — architecture and internals.*
