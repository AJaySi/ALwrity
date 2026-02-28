# Stripe Billing & Subscriptions – Ops Team Guide

This guide is for non-technical operations and support staff. It explains how to use ALwrity’s internal Stripe tools to review payments, handle disputes, and respond to early fraud warnings.

You do **not** need to use the Stripe Dashboard for day-to-day work; use the internal tools described here.

---

## 1. Where to go in the app

- Sign in to ALwrity with your admin account.
- Open the internal Stripe dashboard:
  - URL: `/stripe-disputes`
- You will see two tabs:
  - **Disputes** – for chargebacks / disputes raised by card issuers.
  - **Fraud Warnings** – for early fraud warnings (EFWs) where issuers suspect fraud before a dispute is filed.

If you cannot access this page:

- Your account might not be whitelisted as an admin. Contact the engineering team to check your email and role.

---

## 2. Disputes Tab – Handling Chargebacks

When a customer disputes a payment with their bank, Stripe creates a **Dispute**. The Disputes tab helps you:

- See all disputes.
- Review details (amount, reason, charge ID).
- Submit evidence.
- Close disputes when needed.

### 2.1 Disputes List

The table shows:

- **ID** – Stripe’s dispute ID (useful if support needs to talk to Stripe).
- **Amount** – Disputed amount.
- **Status** – Current status (e.g. `needs_response`, `under_review`, `won`, `lost`).
- **Reason** – Bank’s reason (e.g. `fraudulent`, `product_not_received`).
- **Charge** – The related Stripe charge ID.
- **Created** – When the dispute was created.

Actions:

- **Refresh disputes** – Reloads the list from Stripe.
- **Details** – Opens the dispute details dialog.
- **Close** – Shortcut to close the dispute (same as “Close Dispute” inside the dialog).

### 2.2 Dispute Details & Evidence

When you click **Details**, you see:

- **ID / Amount / Status / Reason / Charge / Created** – Basic information summarizing the case.
- **Fraud Type** – A dropdown where you classify the dispute:
  - `Card testing` – many small rapid attempts, usually bots testing cards.
  - `Stolen card` – customer’s card was used without permission.
  - `Overpayment fraud` – customer overpays and asks for a refund via another method.
  - `Alternative refund` – customer tries to get a payout via cash/crypto/bank transfer instead of back to card.
  - `Other` – anything else.
- **Customer Email / Name / IP** – Fields to record known customer details.
- **Access Activity Log** – Summary of account activity:
  - Example:
    - `"User logged in from IP 1.2.3.4, created 3 projects, downloaded 2 reports."`
- **Fraud Indicators / Notes** – A free text area where you:
  - Summarize what looks suspicious (or legitimate).
  - Mention patterns like:
    - Many failed attempts before one success.
    - Overpayment + request for alternate refund.
    - Different billing and login locations.

Buttons:

- **Submit Evidence**
  - Sends your evidence to Stripe for this dispute.
  - Use this when you want to **contest** the dispute and show that the charge is valid.
- **Close Dispute**
  - Tells Stripe you are not going to submit more evidence.
  - Use this if:
    - The dispute is clearly correct (e.g. genuine mistake).
    - The amount is lower than the dispute fee and not worth contesting.

Tips:

- Be specific and factual in evidence:
  - “User logged in and used the product for 3 days” is better than “Looks fine”.
- Use the **Fraud Type** dropdown to tag cases consistently; it helps the team see patterns.

---

## 3. Fraud Warnings Tab – Early Fraud Warning (EFW)

An **Early Fraud Warning** is a signal from the card issuer that a charge may be fraudulent, before a dispute is created.

The Fraud Warnings tab helps you:

- See EFWs for our charges.
- Decide whether to proactively refund to avoid a later dispute.
- Record decisions and notes.

### 3.1 Fraud Warnings List

Columns:

- **ID** – The Early Fraud Warning ID from Stripe.
- **Charge** – Related Stripe charge ID.
- **Amount** – Charge amount.
- **Status** – Our internal status:
  - `open` – Needs review.
  - `refunded` – We proactively refunded the card.
  - `ignored` – We reviewed and decided not to refund.
- **Action** – The latest action taken (`none`, `refund_full`, `ignored`).
- **Created** – When the warning was created.

Actions:

- **Refresh warnings** – Reloads current open warnings.
- **Details** – Opens the warning details dialog.

### 3.2 Fraud Warning Details and Actions

Inside the details dialog you see:

- **ID / Charge / Amount** – Basic reference info.
- **Status / Action** – Current state and last action taken.
- **Created / Last Action At** – Timeline.
- **Issuer Fraud Type** – What the bank believes is happening (e.g. `made_with_stolen_card`).
- **Actionable** – Indicates whether Stripe considers this warning still actionable:
  - “Yes” – No full refund yet and no dispute; you can still act.
  - “No” – It has either been refunded or disputed already.
- **Action Notes** – Free text for internal reasoning.

Buttons:

- **Refund Full Amount**
  - Sends a full refund for the underlying charge via Stripe.
  - Sets status to `refunded` and action to `refund_full`.
  - Use this when:
    - The charge amount is relatively small (similar to or less than your dispute fee).
    - The warning and behavior strongly suggest fraud (e.g. stolen card, clear card testing).
- **Mark as Ignored**
  - Marks the warning as `ignored` without refund.
  - Use this when:
    - You believe the charge is legitimate.
    - The user has confirmed the purchase, or your internal logs show normal behavior.
- **Close**
  - Closes the dialog only (no changes to Stripe or status).

Notes:

- You can add or update **Action Notes** before clicking Refund or Mark as Ignored:
  - Example:
    - `"Customer confirmed via support email that they made this purchase."`
    - `"High risk: many failed attempts, unusual IP, amount small – refunding to avoid dispute."`

---

## 4. How to Decide: Refund vs Ignore

These are general guidelines; when in doubt, coordinate with product/engineering.

### 4.1 When to Consider Proactive Refund

- The amount is **small**, roughly in the range of the expected dispute fee.
- The pattern clearly matches fraud:
  - Many rapid attempts with different cards or card numbers.
  - Charge is from a suspicious IP/country inconsistent with user profile.
  - Issuer fraud type suggests stolen or counterfeit card.
- The user is not reachable or does not respond to your messages.

In these cases:

- Use **Fraud Warnings → Details → Refund Full Amount**.
- Add a short note explaining why:
  - `"EFW flagged as made_with_stolen_card; small charge; refunding proactively."`

### 4.2 When to Ignore (No Proactive Refund)

- The customer confirms they made the purchase.
- Your logs show normal use of the product:
  - Regular logins, content creation, downloads.
- Amount is large and there is no strong sign of fraud:
  - In this case you typically wait and, if a dispute occurs, respond with strong evidence.

In these cases:

- Use **Fraud Warnings → Details → Mark as Ignored**.
- Add notes:
  - `"Customer confirmed via email; usage patterns normal; ignoring EFW."`

---

## 5. Things You Should Not Do

- Do **not** send refunds via:
  - Bank transfer
  - Cash
  - Crypto
  - Any method outside Stripe

Always refund via Stripe so:

- The cardholder is repaid correctly.
- Issuers see the refund related to the original charge.

If someone asks for a different refund method, treat it as a potential **overpayment** or **alternative refund** scam and escalate to the team.

---

## 6. When to Escalate to Engineering

Contact engineering when:

- You see a sudden **spike in disputes** or fraud warnings.
- The internal dashboard shows errors when:
  - Loading disputes/fraud warnings.
  - Submitting evidence.
  - Refunding/ignoring warnings.
- You need a new flow:
  - Example: new product or plan changes that alter how subscriptions work.

Provide:

- Screenshot of the issue.
- Dispute ID or Fraud Warning ID.
- A short description of what you were trying to do.

---

## 7. Quick Reference

- **Disputes Tab**
  - Use to respond to formal disputes.
  - Add evidence and close disputes when appropriate.
- **Fraud Warnings Tab**
  - Use to review early fraud warnings.
  - Decide whether to refund or ignore.
- **Action Notes**
  - Always record a short reason when you refund or ignore.

If you follow this guide, you will help protect the business from fraud while treating legitimate customers fairly.

