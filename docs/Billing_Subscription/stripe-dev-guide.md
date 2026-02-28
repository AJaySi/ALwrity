# Stripe Billing & Subscriptions – Developer Guide

This document explains how Stripe is integrated into ALwrity for subscriptions, billing, disputes, and fraud handling. It is aimed at developers working on the backend and frontend.

---

## 1. High-Level Architecture

- **Backend**
  - Core service: `StripeService`  
    - File: `backend/services/subscription/stripe_service.py`
  - Subscription/payment API routes:
    - `backend/api/subscription/routes/payment.py`
    - `backend/api/subscription/routes/disputes.py`
    - `backend/api/subscription/routes/fraud_warnings.py`
  - Models:
    - `UserSubscription`, `SubscriptionPlan`, `BillingCycle`, `UsageStatus`, `FraudWarning`  
      - File: `backend/models/subscription_models.py`
- **Frontend**
  - Pricing and checkout UI:
    - `frontend/src/components/Pricing/PricingPage.tsx`
  - Internal admin dashboards:
    - `frontend/src/pages/StripeDisputesDashboard.tsx`
  - Routing:
    - `frontend/src/App.tsx` (route at `/stripe-disputes`)

Data flows:

- Public users:
  - Browse pricing → select plan → start Stripe Checkout → complete subscription.
- Admin/internal users:
  - Use `/stripe-disputes` dashboard to manage disputes and early fraud warnings.

---

## 2. Configuration & Environment

Required environment variables (backend):

- `STRIPE_SECRET_KEY`
  - Stripe API key (test or live).
- `STRIPE_WEBHOOK_SECRET`
  - Webhook signing secret for subscription webhooks.
- `ADMIN_EMAILS` (optional)
  - Comma-separated list of admin emails allowed to access dispute/fraud endpoints.
- `ADMIN_EMAIL_DOMAIN` (optional)
  - Domain considered admin (e.g. `example.com`).
- `DISABLE_AUTH` (optional)
  - If `"true"`, bypasses admin checks for local/testing use only.

Stripe configuration:

- Price IDs are mapped in code (see below) and must exist in the configured Stripe account.
- Webhook endpoint must be configured in Stripe Dashboard:
  - Path: `/api/subscription/webhook`
  - Events: `checkout.session.completed`, `invoice.payment_succeeded`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`, `radar.early_fraud_warning.created` (and optionally `radar.early_fraud_warning.updated`).

---

## 3. Plans, Prices and Mapping

Stripe price mapping lives in `StripeService`:

- File: `backend/services/subscription/stripe_service.py`

Key structures:

- `STRIPE_PLAN_PRICE_MAPPING`
  - Maps `(SubscriptionTier, BillingCycle)` → Stripe `price_id`.
- `STRIPE_PRICE_TO_PLAN`
  - Reverse map: `price_id` → `{ tier, billing_cycle }`.

Helper methods:

- `_get_price_id_for_plan(tier, billing_cycle) -> str`
  - Used when creating Checkout sessions.
- `_get_plan_for_price_id(price_id) -> (SubscriptionPlan, BillingCycle)`
  - Used when mapping Stripe subscription items back into our internal `SubscriptionPlan`.

### Adding or updating plans

1. Create prices in Stripe (with correct recurring configuration).
2. Update `STRIPE_PLAN_PRICE_MAPPING` with new price IDs.
3. Ensure a `SubscriptionPlan` row exists in the DB for the tier being mapped.
4. Redeploy backend with updated mapping.

---

## 4. Checkout and Subscription Lifecycle

### 4.1 Create Checkout Session

Endpoint:

- `POST /api/subscription/create-checkout-session`
  - File: `backend/api/subscription/routes/payment.py`

Request body:

- `tier: SubscriptionTier` (e.g. `"basic"`, `"pro"`)
- `billing_cycle: BillingCycle` (e.g. `"monthly"`)
- `success_url: str`
- `cancel_url: str`

Flow:

1. Auth middleware resolves `current_user` and `user_id`.
2. `StripeService.create_checkout_session`:
   - Fetches `price_id` via `_get_price_id_for_plan`.
   - Finds or creates Stripe Customer (with `user_id` in metadata).
   - Creates a Stripe Checkout Session:
     - Mode: `subscription`.
     - Metadata: includes `user_id` and `price_id`.
3. Returns `checkout_session.url` to the frontend.

Special handling:

- Metered prices:
  - For metered prices, `quantity` is omitted to comply with Stripe rules.
  - For non-metered prices, `quantity` is set to `1`.

### 4.2 Customer Portal Session

Endpoint:

- `POST /api/subscription/create-portal-session`

Flow:

1. Lookup `UserSubscription` and `stripe_customer_id`.
2. If missing, search Stripe by `metadata['user_id']`.
3. Create Stripe Billing Portal session and return URL.

### 4.3 Webhook Handling

Endpoint:

- `POST /api/subscription/webhook`
  - File: `backend/api/subscription/routes/payment.py`
  - Delegates to `StripeService.handle_webhook`.

Verification:

- `stripe.Webhook.construct_event(payload, sig_header, STRIPE_WEBHOOK_SECRET)` is used to validate signatures.

Handled events:

- `checkout.session.completed`
  - Retrieves subscription and price.
  - Updates `UserSubscription` to active and stores `stripe_customer_id` and `stripe_subscription_id`.
- `invoice.payment_succeeded`
  - Sets `UserSubscription.status` to `ACTIVE`.
  - Updates `current_period_end` from invoice period.
- `invoice.payment_failed`
  - Sets status to `PAST_DUE`, `is_active` false.
- `customer.subscription.updated`
  - Syncs status and `auto_renew`.
- `customer.subscription.deleted`
  - Marks subscription as cancelled and disables auto renew.

Helper:

- `_update_user_subscription` centralizes updating/creating `UserSubscription` records based on Stripe data.

---

## 5. Disputes Integration

Backend routes:

- File: `backend/api/subscription/routes/disputes.py`

Endpoints:

- `GET /api/subscription/disputes`
  - Proxies `stripe.Dispute.list`.
- `GET /api/subscription/disputes/{dispute_id}`
  - Proxies `stripe.Dispute.retrieve`.
- `POST /api/subscription/disputes/{dispute_id}`
  - Proxies `stripe.Dispute.modify` with `evidence`.
- `POST /api/subscription/disputes/{dispute_id}/close`
  - Proxies `stripe.Dispute.close`.

Admin guard:

- `_ensure_admin(current_user)` ensures:
  - Admin by email, domain, or role `"admin"`.
  - Can be bypassed only when `DISABLE_AUTH=true` (local use).

Frontend UI:

- File: `frontend/src/pages/StripeDisputesDashboard.tsx`
- Route: `/stripe-disputes`
- Disputes tab:
  - Lists disputes and allows:
    - Viewing details.
    - Submitting evidence fields:
      - `customer_email_address`, `customer_name`, `customer_purchase_ip`, `access_activity_log`, `uncategorized_text`.
    - Tagging a high-level fraud type, which is encoded into `uncategorized_text`.
    - Closing the dispute.

---

## 6. Early Fraud Warnings (EFW) and Proactive Refunds

### 6.1 Ingestion

Model:

- `FraudWarning` in `backend/models/subscription_models.py`
  - Columns: `id`, `charge_id`, `payment_intent_id`, `user_id`, `amount`, `currency`, `status`, `action`, `action_at`, `reason_notes`, `metadata`, `created_at`.

Ingestion logic:

- `StripeService._handle_early_fraud_warning`:
  - Triggered for event types starting with `radar.early_fraud_warning.`.
  - Retrieves the associated `Charge` to populate amount, currency, and metadata.
  - Infers `user_id` from `charge.metadata.user_id` when available.
  - Upserts a `FraudWarning` row with status `"open"` and action `"none"`.
  - Stores raw EFW and Charge data in `metadata`.

### 6.2 Fraud Warnings API

File: `backend/api/subscription/routes/fraud_warnings.py`

Endpoints:

- `GET /api/subscription/fraud-warnings`
  - Query params:
    - `status` (default `"open"`)
    - `limit`, `offset`
  - Returns a list of warnings with core fields.
- `GET /api/subscription/fraud-warnings/{id}`
  - Returns full details including `metadata`.
- `POST /api/subscription/fraud-warnings/{id}/refund`
  - Performs a **full refund** via `stripe.Refund.create(charge=...)`.
  - Updates `status="refunded"`, `action="refund_full"`, `action_at` and `reason_notes`.
- `POST /api/subscription/fraud-warnings/{id}/ignore`
  - Sets `status="ignored"`, `action="ignored"`, updates notes.

All endpoints apply the same admin guard used for disputes.

### 6.3 Frontend Fraud Warnings Tab

- File: `frontend/src/pages/StripeDisputesDashboard.tsx`

Behavior:

- Adds a tabbed view:
  - Tab 1: Disputes.
  - Tab 2: Fraud Warnings.
- Fraud Warnings tab:
  - Lists EFWs (from `/fraud-warnings`).
  - Shows details including:
    - Stripe EFW `fraud_type`, `actionable` flag.
    - Amount, created time, internal status/action.
  - Allows:
    - Proactive full refund (calls `/fraud-warnings/{id}/refund`).
    - Mark as ignored (calls `/fraud-warnings/{id}/ignore`).
    - Add/update internal notes.

---

## 7. Rate Limiting for Checkout

Endpoint: `POST /api/subscription/create-checkout-session`

File: `backend/api/subscription/routes/payment.py`

Logic:

- Per-user in-memory rate limiting:
  - Window: 60 seconds.
  - Max requests: 10 within the window.
  - On exceed:
    - Logs a warning with `user_id`, IP, attempts count.
    - Returns HTTP 429 with a friendly error message.

Purpose:

- Protects against card testing and abuse by limiting how often a user can create Checkout sessions.

Considerations:

- For multi-instance deployments, a shared store (e.g. Redis) is recommended to make rate limiting consistent across instances.

---

## 8. Extending and Maintaining the Integration

### Adding new subscription tiers or prices

1. Create or update prices in Stripe.
2. Update `STRIPE_PLAN_PRICE_MAPPING` in `StripeService`.
3. Ensure corresponding rows in `SubscriptionPlan`.
4. Add any needed frontend logic (e.g. additional tiers in pricing UI).

### Supporting additional Stripe events

- Extend `StripeService.handle_webhook` with new event types.
- Implement corresponding handlers (`_handle_*`) that:
  - Parse event data.
  - Update your DB models.
  - Log with enough context.

### Making the system more robust

- Reintroduce idempotency keys for write operations (Checkout creation, refunds) using stable dedupe keys.
- Replace in-memory rate limiting with shared store-based limiting when scaling horizontally.
- Add more detailed logs/metrics around:
  - New subscriptions.
  - Failed payments.
  - Disputes and early fraud warnings.

