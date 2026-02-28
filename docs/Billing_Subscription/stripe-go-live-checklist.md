# Stripe Go-Live Checklist

This checklist is for preparing ALwrity’s Stripe integration for production. Use it before switching to live keys or onboarding real customers.

Tick each item as you complete it.

---

## 1. Configuration & Environment

- [ ] **Separate environments set up**
  - [ ] Test mode Stripe account configured.
  - [ ] Live mode Stripe account configured.
- [ ] **Environment variables configured for production**
  - [ ] `STRIPE_SECRET_KEY` set to **live** secret key.
  - [ ] `STRIPE_WEBHOOK_SECRET` set to **live** webhook signing secret.
  - [ ] `ADMIN_EMAILS` configured with correct admin emails (comma-separated).
  - [ ] `ADMIN_EMAIL_DOMAIN` configured if using domain-based admin access.
  - [ ] `DISABLE_AUTH` is **not** set to `"true"` in production.
- [ ] **Secrets handling**
  - [ ] No Stripe keys are committed to the repo.
  - [ ] Secrets are stored only in your deployment platform / secret manager.

---

## 2. Prices, Plans and Mapping

- [ ] **All required prices exist in Stripe (live)**
  - [ ] BASIC monthly price created.
  - [ ] PRO monthly price created (if used).
  - [ ] Yearly prices created if you plan to sell yearly plans.
- [ ] **Price mapping in backend updated**
  - [ ] `STRIPE_PLAN_PRICE_MAPPING` uses **live** price IDs (not test IDs).
  - [ ] Mapping covers all tiers and billing cycles you intend to offer.
- [ ] **SubscriptionPlan data is consistent**
  - [ ] DB has `SubscriptionPlan` rows for each tier (BASIC/PRO/etc.).
  - [ ] `is_active` is set to true for sellable plans.

---

## 3. Database & Migrations

- [ ] **Model changes applied in production DB**
  - [ ] Tables related to subscriptions exist:
    - [ ] `subscription_plans`
    - [ ] `user_subscriptions`
  - [ ] Usage/billing tables exist if used (`api_usage_logs`, `usage_summaries`, etc.).
  - [ ] `fraud_warnings` table exists for early fraud warnings:
    - [ ] Checked via DB console or migration logs.
- [ ] **Migration strategy verified**
  - [ ] Any migration scripts run successfully on staging.
  - [ ] Same process is planned for production.

---

## 4. Webhook Setup

- [ ] **Production webhook endpoint configured in Stripe Dashboard**
  - [ ] URL points to your production backend:
    - e.g. `https://your-domain.com/api/subscription/webhook`
  - [ ] Uses HTTPS.
- [ ] **Subscribed events include at least**
  - [ ] `checkout.session.completed`
  - [ ] `invoice.payment_succeeded`
  - [ ] `invoice.payment_failed`
  - [ ] `customer.subscription.updated`
  - [ ] `customer.subscription.deleted`
  - [ ] `radar.early_fraud_warning.created`
  - [ ] (Optional) `radar.early_fraud_warning.updated`
- [ ] **Webhook secret set correctly**
  - [ ] Copy live webhook signing secret from Stripe into `STRIPE_WEBHOOK_SECRET`.
  - [ ] Confirm no test webhook secret is used in production.
- [ ] **Webhook endpoint health check**
  - [ ] Trigger a test event from Stripe Dashboard (in a safe environment).
  - [ ] Verify the backend logs show successful verification and handling.

---

## 5. Internal Admin Tools (Ops Readiness)

- [ ] **Admin roles/permissions**
  - [ ] Confirm at least one admin user can access `/stripe-disputes`.
  - [ ] Non-admin users cannot access sensitive endpoints (disputes, fraud warnings).
- [ ] **Disputes dashboard**
  - [ ] `/stripe-disputes` loads without error.
  - [ ] Disputes tab can:
    - [ ] List disputes.
    - [ ] Show dispute details.
    - [ ] Submit evidence.
    - [ ] Close a dispute.
- [ ] **Fraud Warnings tab**
  - [ ] Fraud Warnings tab loads without error.
  - [ ] List of early fraud warnings is visible when test EFWs exist.
  - [ ] Details dialog shows:
    - [ ] Issuer fraud type.
    - [ ] Actionable flag.
    - [ ] Internal status / actions.
  - [ ] Buttons:
    - [ ] “Refund Full Amount” works (in test/staging).
    - [ ] “Mark as Ignored” works (updates status).
- [ ] **Ops team trained**
  - [ ] Ops have read the Ops Guide.
  - [ ] They understand:
    - [ ] How to respond to disputes.
    - [ ] When to proactively refund EFWs.
    - [ ] When to escalate to engineering.

---

## 6. Manual Test Flows (Before Real Customers)

Perform these in **test** environment first, then in live with small amounts.

### 6.1 New Subscription Flow

- [ ] As a test user:
  - [ ] Go to Pricing page.
  - [ ] Select BASIC monthly (or equivalent).
  - [ ] Start Stripe Checkout and complete payment with test card.
  - [ ] You are redirected back to the success URL.
- [ ] Backend:
  - [ ] Webhook logs show `checkout.session.completed` processed.
  - [ ] `UserSubscription` updated with `stripe_customer_id` and `stripe_subscription_id`.
  - [ ] Subscription status is `ACTIVE`.

### 6.2 Billing Portal

- [ ] From the app, open the billing portal (Customer Portal).
  - [ ] `/api/subscription/create-portal-session` returns a URL.
  - [ ] You can:
    - [ ] View invoices.
    - [ ] Update card details.
    - [ ] Cancel a subscription.
- [ ] After cancellation:
  - [ ] Webhook logs show `customer.subscription.deleted`.
  - [ ] `UserSubscription` is updated to cancelled and not active.

### 6.3 Failed Payment (Test Mode)

- [ ] Use a known failing test card.
- [ ] Trigger a failed invoice.
- [ ] Verify:
  - [ ] `invoice.payment_failed` processed.
  - [ ] `UserSubscription` status is set to `PAST_DUE` and `is_active` is false.

### 6.4 Dispute (Test Mode)

- [ ] Create a test dispute in Stripe’s test mode.
- [ ] Confirm:
  - [ ] Dispute appears in the Disputes tab.
  - [ ] You can open details and submit evidence.

### 6.5 Early Fraud Warning (Test Mode)

- [ ] Create a test Early Fraud Warning (if supported in test mode or via Stripe tools).
- [ ] Confirm:
  - [ ] EFW is ingested and appears in Fraud Warnings tab.
  - [ ] Details dialog shows issuer `fraud_type` and `actionable` flag.
  - [ ] “Refund Full Amount” works in test (Stripe shows charge refunded).

---

## 7. Rate Limiting and Abuse Protection

- [ ] **Checkout endpoint rate limiting**
  - [ ] Confirm `create-checkout-session` applies per-user rate limits.
  - [ ] Hitting the endpoint rapidly produces HTTP 429 and a log entry.
- [ ] **Monitoring for card testing**
  - [ ] Logs for rate-limited events are visible in your logging system.
  - [ ] You have a plan to investigate suspicious spikes (many 429s or many failed payments).

---

## 8. Monitoring & Alerts

- [ ] **Logging**
  - [ ] Backend logs are centralized (e.g. in a logging service).
  - [ ] Key Stripe flows (webhooks, disputes, fraud warnings) log useful context.
- [ ] **Basic alerting**
  - [ ] At minimum, you can detect:
    - [ ] Webhook failures.
    - [ ] Unusually high dispute volume.
    - [ ] Frequent early fraud warnings.

---

## 9. Final Production Switch

- [ ] **Keys double-checked**
  - [ ] Production environment uses live Stripe keys and webhook secret.
  - [ ] No references to test keys remain in production configs.
- [ ] **Test charge in live mode**
  - [ ] Complete a small real transaction in live mode.
  - [ ] Verify:
    - [ ] Subscription is active.
    - [ ] Internal dashboard reflects the subscription correctly.
    - [ ] Refund/portal flows work as expected.
- [ ] **Ops sign-off**
  - [ ] Ops team confirms they can use Disputes and Fraud Warnings tools comfortably.

Once all items are checked, you can consider the Stripe integration ready for production traffic.

