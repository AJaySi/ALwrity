# Outreach Operations

Outreach operations handle the sending pipeline: policy validation, SMTP delivery, idempotency, suppression, and audit logging.

## Send Pipeline

Every outbound email goes through this pipeline:

```mermaid
flowchart TD
    A[Send Request] --> B[Authenticate User]
    B --> C[Resolve Lead Email from DB]
    C --> D[Policy Validation]
    D -->|Approved| E[Create Outreach Attempt Record]
    D -->|Blocked|     F[Record Audit Log + Return 403]
    E --> G[Reserve Daily Cap Slots Atomically]
    G --> H[Send via SMTP with TLS + Message-ID]
    H -->|Success| I[Store Message-ID on Attempt Record]
    H -->|Success| J[Mark Idempotency Key]
    H -->|Success| K[Update Lead Status to Contacted]
    H -->|Failure| L[Return 500 with Generic Error]
    I --> M[Return 200 with Attempt Details]
    J --> M
    K --> M
    
    style D fill:#fff3e0
    style G fill:#e3f2fd
    style F fill:#ffebee
```

!!! warning "Counter timing"
    Daily cap slots are **reserved atomically before sending** via `try_increment_user_send_counter` and `try_increment_domain_send_counter`. If SMTP delivery fails, one slot is consumed (the cap check and increment happen in the same transaction). Idempotency keys are marked only after successful delivery.

## Policy Validation

Before every send, the system validates:

| Check | Rule | On Failure |
|---|---|---|
| **Daily user cap** | Max 100 emails/user/day | Block + audit |
| **Daily domain cap** | Max 20 emails/domain/day | Block + audit |
| **Suppression list** | Recipient not suppressed | Block + audit |
| **Idempotency** | No duplicate `(sender, recipient, subject)` in 24h | Block + audit |
| **Sender alias** | `sender_email` must match `SMTP_ALLOWED_FROM_EMAILS` pattern | Block + fallback to `SMTP_FROM_EMAIL` |
| **Legal basis** | EU domains → "consent", others → "legitimate_interest" | Auto-assign |

**API:** `POST /api/v1/backlink-outreach/policy/validate`

```json
{
  "recipient_email": "editor@example.com",
  "sender_email": "outreach@yourdomain.com",
  "subject": "Guest Post: AI Marketing Trends"
}
```

**Response:**

```json
{
  "allowed": true,
  "reason": "All checks passed",
  "legal_basis": "legitimate_interest",
  "daily_user_count": 23,
  "daily_user_limit": 100,
  "daily_domain_count": 5,
  "daily_domain_limit": 20,
  "region": "US"
}
```

### Region-Aware Legal Basis

The system infers the recipient's region from their email domain's TLD:

| TLDs | Region | Legal Basis |
|---|---|---|
| `.de`, `.fr`, `.it`, `.es`, `.nl`, `.pl`, `.se`, `.at`, `.be`, `.ch`, `.pt`, `.ie`, `.dk`, `.fi`, `.no`, `.cz`, `.gr`, `.hu`, `.ro`, `.bg`, `.hr`, `.sk`, `.si`, `.lt`, `.lv`, `.ee` | EU | `consent` |
| `.co.uk`, `.uk` | UK | `consent` |
| `.ca` | CA | `consent` |
| `.com.au`, `.co.nz` | AU/NZ | `consent` |
| All others | — | `legitimate_interest` |

!!! note "GDPR compliance"
    EU, UK, CA, and AU domain leads always use `consent` as the legal basis. This means you should have obtained some form of consent before reaching out. For other regions, `legitimate_interest` is applied automatically.

## Suppression List

Recipients on the suppression list are blocked from receiving emails.

### Adding to Suppression

**API:** `POST /api/v1/backlink-outreach/suppression`

```json
{
  "email": "unsubscribed@example.com",
  "reason": "User requested unsubscribe"
}
```

### Listing Suppressed Recipients

**API:** `GET /api/v1/backlink-outreach/suppression`

### Auto-Suppression

Recipients are automatically added to the suppression list when:
- They reply with "not interested" language.
- They explicitly request to be removed.
- An email to their address hard-bounces.

## Idempotency

The system prevents duplicate sends using idempotency keys derived from `(sender_email, recipient_email, subject)`.

- Keys are valid for 24 hours.
- After successful SMTP delivery, the key is marked as used.
- Attempting to send the same `(sender, recipient, subject)` within 24h returns a policy block.

## SMTP Configuration

Emails are sent via SMTP with mandatory TLS:

| Setting | Env Var | Default |
|---|---|---|
| SMTP host | `SMTP_HOST` | — (required) |
| SMTP port | `SMTP_PORT` | `587` |
| SMTP username | `SMTP_USER` | — (required) |
| SMTP password | `SMTP_PASS` | — (required) |
| TLS verification | `SMTP_VERIFY_TLS` | `true` |
| Send timeout | `SMTP_SEND_TIMEOUT` | `30` seconds |
| From email | `SMTP_FROM_EMAIL` | — (required) |

!!! warning "TLS certificate verification"
    By default, `SMTP_VERIFY_TLS=true` validates the SMTP server's TLS certificate. Set to `false` only for local development with self-signed certs. **Never disable in production.**

### SMTP Connection Flow

1. Connect to SMTP host on configured port.
2. Send `EHLO` greeting.
3. Upgrade to TLS with `STARTTLS`.
4. Send `EHLO` again (required by RFC 3207 after STARTTLS).
5. Authenticate with username/password.
6. Send the email with a configurable timeout.
7. Quit the connection cleanly.

## Audit Logging

Every policy check is recorded in the audit log:

| Field | Description |
|---|---|
| `user_id` | Authenticated user who initiated the send. |
| `lead_email` | Intended recipient. |
| `sender_email` | Sending address. |
| `subject` | Email subject line. |
| `policy_result` | `approved` or `blocked`. |
| `reason` | Human-readable explanation. |
| `legal_basis` | `consent` or `legitimate_interest`. |
| `timestamp` | When the check occurred. |

---

*Next: [Reply Inbox](reply-inbox.md) — IMAP monitoring and auto-classification.*
