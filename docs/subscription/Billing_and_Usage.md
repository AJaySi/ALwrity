# Subscription, Billing & Usage Tracking

This document details how ALwrity manages subscriptions, processes payments via Stripe, and tracks granular usage for every user interaction.

## 1. Subscription Model

ALwrity uses a **tier-based subscription model** enforced at the API gateway level.

### Tiers
- **Free**: Limited access, community support.
- **Basic**: Entry-level AI usage, standard support.
- **Pro**: High limits, advanced models (Gemini Pro, FLUX), priority support.
- **Enterprise**: Custom limits, dedicated infrastructure.

### Data Model (`UserSubscription`)
Stored in the user's SQLite database (`alwrity_user_{id}.db`):
- `stripe_customer_id`: Link to Stripe Customer.
- `stripe_subscription_id`: Active subscription ID.
- `plan_id`: Internal plan reference (linked to `SubscriptionPlan`).
- `status`: `active`, `past_due`, `canceled`, etc.
- `current_period_start` / `end`: Defines the billing cycle window.

## 2. Billing Integration (Stripe)

We use **Stripe** for all payments, webhooks, and portal management.

### Key Components
- **StripeService**: Handles checkout creation, portal sessions, and webhooks.
- **Webhooks**: Listens for events like `invoice.payment_succeeded`, `customer.subscription.updated`.
  - **Idempotency**: All webhooks are tracked in `ProcessedStripeEvent` to prevent duplicate processing.
  - **Reliability**: Events are processed transactionally; failures are logged and retried by Stripe.
- **Configuration**: Plan-to-Price mapping is loaded from environment variables (`STRIPE_PLAN_PRICE_MAPPING_TEST` / `_LIVE`) to ensure sync between code and Stripe Dashboard.

### Checkout Flow
1. Frontend calls `/api/subscription/create-checkout-session`.
2. Backend validates user and creates Stripe Session.
3. User pays on Stripe.
4. Stripe sends `checkout.session.completed` webhook.
5. Backend provisions subscription and credits in `UserSubscription`.

## 3. Usage Tracking

Every API call to an LLM provider is tracked, costed, and logged.

### Tracking Flow
1. **Pre-flight Check** (`check_usage_limits`):
   - Before generating content, the system estimates cost/tokens.
   - If user exceeds plan limits (e.g., "50 videos/month"), the request is rejected (429).
2. **Execution**: The provider generates the content.
3. **Post-execution Log** (`track_usage`):
   - Actual tokens/duration are measured.
   - Cost is calculated based on `APIProviderPricing` table.
   - Entry added to `APIUsageLog` (granular) and aggregated into `UsageSummary` (monthly totals).

### Database Tables
- **`APIUsageLog`**: Immutable ledger of every call.
  - Fields: `user_id`, `provider`, `model`, `input_tokens`, `output_tokens`, `cost`, `status_code`.
- **`UsageSummary`**: Aggregated stats per billing period.
  - Fields: `total_calls`, `total_cost`, `gemini_calls`, `video_calls`, etc.
  - **Unique Constraint**: Enforced on `(user_id, billing_period)` to prevent data drift.

### Pricing Engine (`PricingService`)
- Costs are not hardcoded. They are fetched from `APIProviderPricing` table.
- Supports per-token (text), per-image (media), and per-second (video/audio) pricing models.
- Admin can update pricing in DB without redeploying code.

## 4. Frontend Integration

- **Usage Dashboard**: Visualizes consumption vs. limits.
- **Real-time**: Usage stats are typically updated immediately after generation.
- **Limit Rings**: UI components show percentage used (e.g., "80% of monthly video limit").
