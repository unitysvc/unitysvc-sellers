# Seller Lifecycle

This guide explains what happens after you upload your services to UnitySVC - from approval through invoicing and payouts.

## Overview

```mermaid
flowchart TD
    subgraph Upload["1. Upload"]
        A[ServiceOffering<br/>What seller offers TO UnitySVC]
        B[ServiceListing<br/>What seller offers TO Users]
    end

    subgraph Review["2. Review"]
        C{UnitySVC Reviews<br/>& Approves}
    end

    subgraph Active["3. Active Service"]
        D[Service activated<br/>visibility: unlisted]
        D2{Seller sets<br/>visibility: public}
        E[Listed on marketplace<br/>Usage tracked]
    end

    subgraph Billing["4. Monthly Billing"]
        F[Invoice generated]
        G{Seller Reviews}
        H[Invoice finalized]
    end

    subgraph Payout["5. Payout"]
        I[Payout window]
        J[Balance available]
        K[Payment processed]
    end

    A --> C
    B --> C
    C -->|Approved| D
    D --> D2
    D2 -->|Published| E
    E --> F
    F --> G
    G -->|No dispute| H
    G -->|Dispute| G
    H --> I
    I --> J
    J --> K
```

## 1. Upload & Approval

When you run `usvc_seller data upload`, you submit:

| Data Type           | Purpose                    | Key Fields                                    |
| ------------------- | -------------------------- | --------------------------------------------- |
| **ServiceOffering** | What you offer TO UnitySVC | Provider info, API access, `payout_price`     |
| **ServiceListing**  | What you offer TO Users    | User-facing info, `list_price`, documentation |

**Pricing Model:**

```mermaid
flowchart LR
    subgraph YourCost["Your Cost (Trade Secret)"]
        A[Provider pricing<br/>e.g., OpenAI rates]
    end

    subgraph Agreement["Seller ↔ UnitySVC"]
        B[payout_price<br/>What you charge UnitySVC]
    end

    subgraph Customer["Customer Facing"]
        C[list_price<br/>What UnitySVC charges users]
    end

    A -.->|Your margin| B
    B -->|UnitySVC margin| C
```

-   **payout_price** is the agreed rate between you and UnitySVC
-   Your actual provider costs are your trade secret - UnitySVC doesn't need to know
-   **list_price** is what end users pay

## 2. Active Service

Once approved by admin, your service is **activated** but starts as **unlisted** — it is live and routable, but not yet visible in the public marketplace catalog.

### Visibility

Every service has a visibility setting that controls catalog presence:

| Visibility | In catalog? | Routable? | Use case |
|---|---|---|---|
| **`unlisted`** (default) | No | Yes | Soft launch — test with beta customers via direct link |
| **`public`** | Yes | Yes | Fully discoverable in the marketplace |
| **`private`** | No | Yes | Internal/ops services, not for customers |

!!! note "Unlisted services are fully functional"
    Unlisted services are not hidden — they are simply not listed in the catalog. Anyone with the direct URL can view the service page, enroll, and use the API without any additional restriction. This makes `unlisted` ideal for sharing with beta customers before a public launch: just send them the link.

**After activation, you must explicitly publish your service** by setting visibility to `public`. This gives you a soft-launch period to:

-   Verify billing and usage tracking work correctly
-   Share the direct link with beta customers for early feedback
-   Confirm documentation and pricing are final

### Publishing your service

**CLI:**

```bash
# Set a single service to public
usvc_seller services update <service-id> --visibility public

# Set all active services to public (bulk)
usvc_seller services set-visibility --all --visibility public --yes
```

**SDK:**

```python
client.services.update(service_id, {"visibility": "public"})
```

**Web interface:** Use the visibility toggle on the service detail page.

You can switch back to `unlisted` at any time to temporarily remove a service from the catalog without affecting existing enrollments or routing.

### Once published

-   **Listed on marketplace** - Users can discover and subscribe
-   **API routing configured** - Requests flow through UnitySVC gateway
-   **Usage metering** - Every request is tracked in real-time

## 3. Monthly Invoicing

At the end of each month, UnitySVC generates your invoice:

```mermaid
flowchart LR
    A[Usage Data] --> B[Calculate:<br/>usage × payout_price]
    B --> C[Generate Invoice]
    C --> D{Dispute Window<br/>1-2 weeks}
    D -->|No Dispute| E[finalized]
    D -->|Dispute| F[Submit Revision]
    F --> G{UnitySVC Reviews}
    G -->|Accept| E
    G -->|Negotiate| F
    E -->|Payout window expires| H[funds_released]
```

### Invoice Contents

Your monthly invoice includes:

| Field               | Description                                |
| ------------------- | ------------------------------------------ |
| **Billing Period**  | Start and end dates (e.g., Jan 1 - Jan 31) |
| **Opening Balance** | Carried forward from previous invoice      |
| **Seller Payout**   | Sum of (usage × payout_price) per service  |
| **Adjustments**     | Any credits or debits applied              |
| **Closing Balance** | Total owed to you                          |

### Line Items

Each service shows:

-   Request count
-   Token usage (input/output)
-   Seller price applied
-   Calculated payout

### Dispute Window

You have **1-2 weeks** to review the invoice:

-   **No action needed** if the invoice is correct - it auto-finalizes
-   **Dispute** if you see issues - submit a revised invoice with justification

**Valid dispute reasons:**

| Reason        | Example                             |
| ------------- | ----------------------------------- |
| Rate change   | "We agreed to lower rate mid-month" |
| Service issue | "Service was down for 2 days"       |
| Billing error | "Usage count looks incorrect"       |

## 4. Payout Process

Invoices track earnings. Actual payouts are handled separately - you can request payouts from your available balance at any time.

```mermaid
flowchart TB
    subgraph Finalize["Invoice: finalized"]
        A[Update current_balance]
    end

    subgraph Window["Payout Window (1-2 months)"]
        B[Balance held for<br/>customer chargebacks]
        C{Any issues?}
        D[Deduct chargebacks]
        E[Window expires]
    end

    subgraph Released["Invoice: funds_released"]
        F[Update available_payout]
    end

    subgraph Payout["Payout (separate from invoices)"]
        G{Payout Trigger}
        H[On-demand request]
        I[Automatic payout]
        J[SellerPayout created]
        K[Payment processed]
    end

    A --> B
    B --> C
    C -->|Chargeback| D
    C -->|No issues| E
    D --> E
    E --> F
    F --> G
    G --> H
    G --> I
    H --> J
    I --> J
    J --> K
```

### Invoice Statuses

| Status           | Description                           | Balance Updated    |
| ---------------- | ------------------------------------- | ------------------ |
| `generated`      | Invoice created, in dispute window    | -                  |
| `disputed`       | You disputed, awaiting review         | -                  |
| `resolved`       | Dispute resolved                      | -                  |
| `finalized`      | Invoice closed                        | `current_balance`  |
| `funds_released` | Payout window expired                 | `available_payout` |
| `voided`         | Invoice voided (fraud/abuse detected) | -                  |

### Balance Fields

Your seller account tracks two balances:

| Field                | Description                                          |
| -------------------- | ---------------------------------------------------- |
| **current_balance**  | Total earnings (closing balance from latest invoice) |
| **available_payout** | Amount available for immediate payout                |

### Payout Window

The payout window (default 2 months) provides time for:

-   Customer dispute resolution
-   Chargeback handling
-   Fraud detection

**Trusted sellers** may receive a shorter payout window as an incentive.

### Payout Modes

| Mode                      | Description                                |
| ------------------------- | ------------------------------------------ |
| **On-demand**             | You request payout of available balance    |
| **Automatic (threshold)** | Payout when balance exceeds your threshold |
| **Automatic (scheduled)** | Payout on your configured schedule         |

### Timeline Example

| Date   | Event                                     | current_balance | available_payout |
| ------ | ----------------------------------------- | --------------- | ---------------- |
| Feb 1  | January invoice generated ($1,000)        | -               | -                |
| Feb 14 | Dispute deadline passes                   | -               | -                |
| Feb 15 | Invoice finalized                         | $1,000          | $0               |
| Mar 15 | February invoice finalized ($1,200)       | $2,200          | $0               |
| Apr 1  | January payout window expires (2 months)  | $2,200          | $1,000           |
| Apr 20 | You request $500 payout                   | $1,700          | $500             |
| May 1  | February payout window expires (2 months) | $1,700          | $1,700           |

## Summary

1. **Upload** your ServiceOffering and ServiceListing
2. **UnitySVC reviews** and approves your submission
3. **Service activated** as `unlisted` — live and routable, not in catalog
4. **Set visibility to `public`** when ready for the marketplace
5. **Monthly invoice** generated based on usage × payout_price
6. **Dispute window** gives you time to review (1-2 weeks)
7. **Payout window** protects against chargebacks (1-2 months)
8. **Payout** when balance becomes available

## Questions?

-   Contact your UnitySVC account manager for billing questions
-   Open an issue on [GitHub](https://github.com/unitysvc/unitysvc-sellers/issues) for SDK questions
