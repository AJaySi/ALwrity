# API Reference

Complete reference for all Backlink Outreach API endpoints. All endpoints require Clerk authentication via `Depends(get_current_user)`.

## Authentication

All endpoints use Clerk authentication. Include the session token in the `Authorization` header:

```
Authorization: Bearer <clerk_session_token>
```

The `user_id` is derived from the authenticated session — never from the request body.

## Endpoint Map

```mermaid
flowchart TD
    subgraph Campaigns
        C1[POST /campaigns]
        C2[GET /campaigns]
        C3[GET /campaigns/{id}]
        C4[DELETE /campaigns/{id}]
    end
    subgraph Leads
        L1[POST /campaigns/{id}/leads]
        L2[POST /campaigns/{id}/leads/bulk]
        L3[PATCH /campaigns/{id}/leads/{lead_id}/status]
        L4[PATCH /campaigns/{id}/leads/bulk-status]
    end
    subgraph Discovery
        D1[POST /discover/deep]
    end
    subgraph Email
        E1[POST /emails/generate]
        E2[POST /emails/personalize]
        E3[POST /emails/subject-suggestions]
        E4[POST /emails/follow-up]
        E5[POST /emails/templates]
        E6[GET /emails/templates]
        E7[GET /emails/templates/{id}]
        E8[DELETE /emails/templates/{id}]
    end
    subgraph Outreach
        O1[POST /outreach/send]
        O2[POST /policy/validate]
        O3[GET /campaigns/{id}/attempts]
        O4[GET /campaigns/{id}/follow-ups]
    end
    subgraph Replies
        R1[POST /replies/poll]
        R2[GET /campaigns/{id}/replies]
    end
    subgraph Suppression
        S1[POST /suppression]
        S2[GET /suppression]
    end
    subgraph Analytics
        A1[GET /campaigns/{id}/analytics]
        A2[GET /reporting/snapshot]
        A3[GET /campaigns/{id}/export/leads]
        A4[GET /campaigns/{id}/export/attempts]
        A5[GET /campaigns/{id}/export/replies]
    end
```

---

## Campaigns

### Create Campaign

`POST /api/v1/backlink-outreach/campaigns`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Campaign name. |
| `description` | string | No | Campaign description. |
| `keywords` | string[] | No | Target keywords for discovery. |

**Response:** `201 Created` — Campaign object.

### List Campaigns

`GET /api/v1/backlink-outreach/campaigns`

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `workspace_id` | string | user_id | Workspace to filter by. Defaults to authenticated user. |

**Response:** `200 OK` — Array of campaign objects.

### Get Campaign

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}`

**Response:** `200 OK` — Campaign object with included leads.

### Delete Campaign

`DELETE /api/v1/backlink-outreach/campaigns/{campaign_id}`

**Response:** `204 No Content`

---

## Leads

### Add Lead

`POST /api/v1/backlink-outreach/campaigns/{campaign_id}/leads`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `website_url` | string | Yes | Target website URL. |
| `website_title` | string | No | Website title. |
| `contact_email` | string | No | Contact email address. |
| `quality_score` | float | No | Quality score (0-1). |
| `relevance_score` | float | No | Relevance score (0-1). |
| `guest_post_likelihood` | float | No | Guest post likelihood (0-1). |
| `source` | string | No | Source of the lead. |

**Response:** `201 Created` — Lead object.

### Bulk Add Leads

`POST /api/v1/backlink-outreach/campaigns/{campaign_id}/leads/bulk`

**Request Body:** Array of lead objects.

**Response:** `200 OK`

| Field | Type | Description |
|---|---|---|
| `added` | int | Number of leads successfully added. |
| `skipped` | int | Number of duplicates skipped. |
| `failed` | string[] | List of failed entries with reasons. |

### Update Lead Status

`PATCH /api/v1/backlink-outreach/campaigns/{campaign_id}/leads/{lead_id}/status`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | string | Yes | New status: discovered, contacted, replied, placed, bounced, lost. |

**Response:** `200 OK` — Updated lead object.

### Bulk Update Status

`PATCH /api/v1/backlink-outreach/campaigns/{campaign_id}/leads/bulk-status`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `lead_ids` | string[] | Yes | Lead IDs to update. |
| `status` | string | Yes | New status for all leads. |

**Response:** `200 OK`

| Field | Type | Description |
|---|---|---|
| `updated` | int | Number of leads successfully updated. |
| `failed` | string[] | List of lead IDs that failed to update. |

!!! warning "Partial failures"
    Bulk operations may partially succeed. Always check the `failed` field and show appropriate warnings to users.

---

## Discovery

### Deep Discovery

`POST /api/v1/backlink-outreach/discover/deep`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `keyword` | string | Yes | Search keyword or phrase. |
| `campaign_id` | string | No | Campaign to save results to. |
| `max_results` | int | No | Maximum results to return (default 20). |
| `save_to_campaign` | bool | No | Auto-save results to campaign. |

**Response:** `200 OK`

| Field | Type | Description |
|---|---|---|
| `results` | array | Discovered opportunities with scores. |
| `saved_to_campaign` | int | Number of leads saved to campaign. |
| `save_failed` | int | Number of leads that failed to save. |

---

## Email

### Generate Email

`POST /api/v1/backlink-outreach/emails/generate`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `topic` | string | Yes | Email topic. |
| `tone` | string | No | professional, friendly, casual, formal. |
| `template_id` | string | No | Template to base generation on. |

**Response:** `200 OK` — `{ subject, body }`

### Personalize Email

`POST /api/v1/backlink-outreach/emails/personalize`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `base_email` | string | Yes | Email content to personalize. |
| `lead_name` | string | No | Lead's name. |
| `lead_website` | string | No | Lead's website. |
| `content_topic` | string | No | Topic to reference. |

**Response:** `200 OK` — `{ subject, body }`

### Subject Suggestions

`POST /api/v1/backlink-outreach/emails/subject-suggestions`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `topic` | string | Yes | Email topic. |
| `tone` | string | No | Tone for suggestions. |

**Response:** `200 OK` — `{ suggestions: string[] }`

### Generate Follow-up

`POST /api/v1/backlink-outreach/emails/follow-up`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `original_subject` | string | Yes | Subject of original email. |
| `original_body` | string | Yes | Body of original email. |
| `tone` | string | No | Tone for follow-up. |

**Response:** `200 OK` — `{ subject, body }`

### Create Template

`POST /api/v1/backlink-outreach/emails/templates`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Template name. |
| `subject` | string | Yes | Subject line with `{placeholders}`. |
| `body` | string | Yes | Email body with `{placeholders}`. |
| `category` | string | No | Template category. |

**Response:** `201 Created` — Template object.

### List Templates

`GET /api/v1/backlink-outreach/emails/templates`

**Response:** `200 OK` — Array of template objects.

### Get Template

`GET /api/v1/backlink-outreach/emails/templates/{template_id}`

**Response:** `200 OK` — Template object.

### Delete Template

`DELETE /api/v1/backlink-outreach/emails/templates/{template_id}`

**Response:** `204 No Content`

---

## Outreach

### Send Outreach

`POST /api/v1/backlink-outreach/outreach/send`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `campaign_id` | string | Yes | Campaign for the outreach. |
| `lead_id` | string | Yes | Lead to send to. |
| `subject` | string | Yes | Email subject. |
| `body` | string | Yes | Email body. |
| `workspace_id` | string | No | Workspace ID (default "default"). |

**Response:** `200 OK` — Outreach attempt object.

**Error responses:**

| Code | Meaning |
|---|---|
| `403` | Policy validation failed (caps, suppression, idempotency). |
| `500` | SMTP delivery failed (generic error, no stack trace). |

### Validate Policy

`POST /api/v1/backlink-outreach/policy/validate`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `recipient_email` | string | Yes | Recipient email address. |
| `sender_email` | string | Yes | Sender email address. |
| `subject` | string | No | Email subject for idempotency check. |

**Response:** `200 OK` — Policy validation result with `allowed`, `reason`, `legal_basis`, counts, and limits.

### List Attempts

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/attempts`

**Response:** `200 OK` — Array of outreach attempt objects.

### List Follow-ups

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/follow-ups`

**Response:** `200 OK` — Array of follow-up objects.

---

## Replies

### Poll Replies

`POST /api/v1/backlink-outreach/replies/poll`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `campaign_id` | string | No | Campaign to filter by. |

**Response:** `200 OK`

| Field | Type | Description |
|---|---|---|
| `replies_found` | int | Number of new replies processed. |
| `failed` | int | Number of replies that failed to process. |

### List Replies

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/replies`

**Response:** `200 OK` — Array of reply objects with classification.

---

## Suppression

### Add to Suppression

`POST /api/v1/backlink-outreach/suppression`

**Request Body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `email` | string | Yes | Email to suppress. |
| `reason` | string | No | Reason for suppression. |

**Response:** `201 Created` — Suppression record.

### List Suppressed

`GET /api/v1/backlink-outreach/suppression`

**Response:** `200 OK` — Array of suppression records.

---

## Analytics

### Campaign Analytics

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/analytics`

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | int | 30 | Days to include in trends. |

**Response:** `200 OK` — Analytics object with leads_by_status, replies_by_classification, rates, and daily_send_volume.

### Reporting Snapshot

`GET /api/v1/backlink-outreach/reporting/snapshot`

**Response:** `200 OK` — Cross-campaign summary with total counts and rates.

### Export Leads

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/export/leads`

**Response:** `200 OK` — CSV file download.

### Export Attempts

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/export/attempts`

**Response:** `200 OK` — CSV file download.

### Export Replies

`GET /api/v1/backlink-outreach/campaigns/{campaign_id}/export/replies`

**Response:** `200 OK` — CSV file download.

---

## Common Error Responses

| Status | Meaning | Body |
|---|---|---|
| `401` | Not authenticated | `{"detail": "Not authenticated"}` |
| `403` | Policy blocked | `{"detail": "Policy validation failed", "reason": "..."}` |
| `404` | Not found | `{"detail": "Resource not found"}` |
| `422` | Validation error | `{"detail": [...validation errors]}` |
| `500` | Server error | `{"detail": "An internal error occurred"}` (generic, no stack trace) |
