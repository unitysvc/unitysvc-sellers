# Pricing Specification

This document describes the pricing structure used for `payout_price` (in service files) and `list_price` (in listing files).

## Overview

UnitySVC uses a two-tier pricing model:

- **Seller Price** (`payout_price` in `offering_v1`): The agreed rate between the seller and UnitySVC. This is what the seller charges UnitySVC for each unit of service usage.
- **Customer Price** (`list_price` in `listing_v1`): The price shown to customers on the marketplace. This is what the customer pays for each unit of service usage.

Both use the same `Pricing` structure, which supports multiple pricing types through a discriminated union based on the `type` field.

> **Important: Use String Values for Prices**
>
> All price values (`price`, `input`, `output`) should be specified as **strings** (e.g., `"0.50"`) rather than floating-point numbers. This avoids floating-point precision issues where values like `2.0` might become `1.9999999` when saved and loaded.

## Multi-Currency Support

Currency is specified at the **service/listing level**, not inside the pricing object:

- **Service** (ServiceOffering): Has ONE `payout_price` with ONE currency
- **Listing** (ServiceListing): Has ONE `list_price` with ONE currency
- **Multiple currencies**: Create multiple listings pointing to the same service

```
ServiceOffering (gpt-4-turbo)
├── payout_price (USD)

ServiceListing (gpt-4-turbo-usd)
├── currency: USD
└── list_price

ServiceListing (gpt-4-turbo-eur)
├── currency: EUR
└── list_price
```

### Currency Field Location

| Level           | Field      | Description                                     |
| --------------- | ---------- | ----------------------------------------------- |
| ServiceOffering | `currency` | Currency for payout_price                       |
| ServiceListing  | `currency` | Currency for list_price (indexed for filtering) |

## Pricing Object Structure

Acceptable fields of the Pricing object are based on the `type` field.

```
Pricing
├── type          (required) - Pricing type discriminator
├── description   (optional) - Human-readable pricing description
├── reference     (optional) - URL to upstream pricing page
└── [type-specific fields]
```

### Common Fields

| Field         | Type   | Required | Description                                     |
| ------------- | ------ | -------- | ----------------------------------------------- |
| `type`        | string | **Yes**  | Pricing type (discriminator)                    |
| `description` | string | No       | Human-readable description of the pricing model |
| `reference`   | string | No       | URL to upstream provider's pricing page         |

---

## Per-Request Pricing Types

These pricing types calculate cost based on usage data from a single API request. They are suitable for both `list_price` and `payout_price`.

**Available metrics for per-request pricing:**

| Metric               | Equivalence Group | Description                   | Source    |
| -------------------- | ----------------- | ----------------------------- | --------- |
| `input_tokens`       | —                 | Number of input tokens        | UsageData |
| `output_tokens`      | —                 | Number of output tokens       | UsageData |
| `total_tokens`       | —                 | Total tokens (input + output) | UsageData |
| `one_token`          | tokens            | Token count (raw)             | UsageData |
| `one_thousand_tokens`| tokens            | Token count (in thousands)    | UsageData |
| `one_million_tokens` | tokens            | Token count (in millions)     | UsageData |
| `seconds`            | time              | Duration in seconds           | UsageData |
| `one_second`         | time              | Duration in seconds           | UsageData |
| `one_minute`         | time              | Duration in minutes           | UsageData |
| `one_hour`           | time              | Duration in hours             | UsageData |
| `one_day`            | time              | Duration in days              | UsageData |
| `one_month`          | time              | Duration in months (30 days)  | UsageData |
| `one_byte`           | data              | Data volume in bytes          | UsageData |
| `one_kilobyte`       | data              | Data volume in KB (1024 B)    | UsageData |
| `one_megabyte`       | data              | Data volume in MB             | UsageData |
| `one_gigabyte`       | data              | Data volume in GB             | UsageData |
| `count`              | count             | Count (images, steps, etc.)   | UsageData |
| `one_thousand`       | count             | Count in thousands            | UsageData |
| `one_million`        | count             | Count in millions             | UsageData |

> **Equivalence Groups:** Metrics in the same equivalence group measure the same dimension and convert automatically. For example, pricing in `one_hour` accepts usage provided in `one_minute` or `seconds`. See [Equivalence Groups](#equivalence-groups) for details.

### Token-Based Pricing (`one_million_tokens`, `one_thousand_tokens`, `one_token`)

For LLM and text-based services. Prices are per unit of tokens at the chosen scale.

**Allowed types:** `one_million_tokens` (default), `one_thousand_tokens`, `one_token`

These types belong to the **tokens** equivalence group — usage provided in any token unit is converted automatically.

**Fields:**

| Field          | Type   | Required    | Description                                         |
| -------------- | ------ | ----------- | --------------------------------------------------- |
| `type`         | string | **Yes**     | `"one_million_tokens"`, `"one_thousand_tokens"`, or `"one_token"` |
| `price`        | string | Auto-computed | Summary price for marketplace comparison and sorting |
| `input`        | string | \*          | Price per unit of input tokens                      |
| `output`       | string | \*          | Price per unit of output tokens                     |
| `cached_input` | string | No          | Price per unit of cached input tokens (discounted)  |

**Pricing modes:**

1. **Unified pricing**: Set `price` only — same rate for all token types. Used for billing.
2. **Separate pricing**: Set `input` and `output` (and optionally `cached_input`). The `price` field is auto-computed as a summary for marketplace comparison if not explicitly set.

**Summary price auto-computation:**

When `input` and `output` are specified without `price`, the system automatically computes:

```
price = (input + 4 × output) / 5
```

This formula weights output tokens 4× higher than input, reflecting typical LLM usage where output tokens are more expensive and represent the dominant cost. Sellers can override by setting `price` explicitly.

**Validation Rules:**

- Must specify either `price` (unified) or both `input` and `output` (separate)
- When using separate pricing, `price` is auto-computed if not set
- Negative values are allowed for `payout_price` (seller-funded incentives)

**Example - Unified Pricing:**

```json
{
    "type": "one_million_tokens",
    "price": "2.50",
    "description": "Per million tokens"
}
```

**Example - Separate Input/Output Pricing:**

```json
{
    "type": "one_million_tokens",
    "input": "3.00",
    "output": "15.00",
    "description": "Claude Sonnet pricing"
}
```

In this example, `price` is auto-computed as `(3 + 4×15) / 5 = 12.60`. The marketplace displays **$12.60 / 1M tokens** for sorting and comparison.

**Example - With Explicit Summary Price:**

```json
{
    "type": "one_million_tokens",
    "price": "9.00",
    "input": "3.00",
    "output": "15.00",
    "description": "Seller-chosen comparison price"
}
```

**Example - Negative Payout (Seller-Funded Incentive):**

```json
{
    "type": "one_million_tokens",
    "input": "-1.00",
    "output": "-5.00",
    "description": "Seller pays platform for free customer access"
}
```

**TOML Example:**

```toml
[list_price]
type = "one_million_tokens"
input = "12.00"
output = "36.00"
description = "Customer token pricing"
# price auto-computed as (12 + 4×36) / 5 = 31.20
```

### Time-Based Pricing (`one_second`, `one_minute`, `one_hour`, `one_day`, `one_month`)

For audio/video processing, compute time, alias duration, and other time-based services.

**Allowed types:** `one_second`, `one_minute`, `one_hour`, `one_day`, `one_month` (30 days)

These types belong to the **time** equivalence group — usage provided in any time unit is converted automatically.

**Fields:**

| Field   | Type   | Required | Description                             |
| ------- | ------ | -------- | --------------------------------------- |
| `type`  | string | **Yes**  | One of the time unit types listed above |
| `price` | string | **Yes**  | Price per one unit of the specified type |

**Example - Per Second:**

```json
{
    "type": "one_second",
    "price": "0.006",
    "description": "Audio transcription per second"
}
```

**Example - Per Month (with cross-unit usage):**

```json
{
    "type": "one_month",
    "price": "1.00",
    "description": "Alias fee per month, prorated by active seconds"
}
```

Usage of `UsageData(one_hour=360)` with this pricing auto-converts: 360 hours / 720 hours per month = 0.5 months = $0.50.

### Image Pricing (`image`)

For image generation, processing, and analysis services.

**Fields:**

| Field   | Type   | Required | Description       |
| ------- | ------ | -------- | ----------------- |
| `type`  | string | **Yes**  | Must be `"image"` |
| `price` | string | **Yes**  | Price per image   |

**Example:**

```json
{
    "type": "image",
    "price": "0.04",
    "description": "DALL-E 3 image generation"
}
```

### Step-Based Pricing (`step`)

For diffusion models, iterative processes, and other step-based services.

**Fields:**

| Field   | Type   | Required | Description              |
| ------- | ------ | -------- | ------------------------ |
| `type`  | string | **Yes**  | Must be `"step"`         |
| `price` | string | **Yes**  | Price per step/iteration |

**Example:**

```json
{
    "type": "step",
    "price": "0.001",
    "description": "Diffusion model steps"
}
```

### Data-Volume Pricing (`one_byte`, `one_kilobyte`, `one_megabyte`, `one_gigabyte`)

For bandwidth, storage, transfer, and other data-volume services. Uses binary units (1 KB = 1024 bytes).

**Allowed types:** `one_byte`, `one_kilobyte`, `one_megabyte` (default), `one_gigabyte`

These types belong to the **data** equivalence group — usage provided in any data unit is converted automatically.

**Fields:**

| Field   | Type   | Required | Description                             |
| ------- | ------ | -------- | --------------------------------------- |
| `type`  | string | **Yes**  | One of the data unit types listed above |
| `price` | string | **Yes**  | Price per one unit of the specified type |

**Example:**

```json
{
    "type": "one_gigabyte",
    "price": "0.10",
    "description": "Data transfer per GB"
}
```

### Count-Scaled Pricing (`one_thousand`, `one_million`)

For API calls, events, requests, and other count-based services at scale. For simple per-item count pricing, use `image` or `step` instead.

**Allowed types:** `one_thousand`, `one_million`

These types belong to the **count** equivalence group (along with `count`) — usage provided as `count`, `one_thousand`, or `one_million` is converted automatically.

**Fields:**

| Field   | Type   | Required | Description                              |
| ------- | ------ | -------- | ---------------------------------------- |
| `type`  | string | **Yes**  | `"one_thousand"` or `"one_million"`      |
| `price` | string | **Yes**  | Price per one unit of the specified type  |

**Example:**

```json
{
    "type": "one_thousand",
    "price": "0.50",
    "description": "Per 1,000 API requests"
}
```

### Constant Pricing (`constant`)

A fixed price per request that doesn't depend on usage metrics.

> **Note:** When used for `list_price`, this price is charged **per API request**. For example, `"price": "0.01"` means the customer pays $0.01 for each request they make.

**Fields:**

| Field    | Type   | Required | Description                                              |
| -------- | ------ | -------- | -------------------------------------------------------- |
| `type`   | string | **Yes**  | Must be `"constant"`                                     |
| `price`  | string | **Yes**  | Fixed price (positive for charge, negative for discount) |

**Example - Per-Request Fee:**

```json
{
    "type": "constant",
    "price": "0.01",
    "description": "Per-request fee"
}
```

---

## Equivalence Groups

Units within the same equivalence group measure the same dimension and convert to each other automatically. When a pricing type specifies one unit (e.g., `one_hour`) but usage data provides a different unit from the same group (e.g., `one_minute`), the system converts automatically before calculating cost.

This applies both to direct pricing types (e.g., `TimePriceData`) and to the `based_on` field in tiered/graduated pricing.

| Group      | Units                                                           | Base Unit | Conversion                |
| ---------- | --------------------------------------------------------------- | --------- | ------------------------- |
| **time**   | `seconds`, `one_second`, `one_minute`, `one_hour`, `one_day`, `one_month` | seconds   | Standard time factors     |
| **tokens** | `one_token`, `one_thousand_tokens`, `one_million_tokens`        | tokens    | ×1, ×1,000, ×1,000,000    |
| **data**   | `one_byte`, `one_kilobyte`, `one_megabyte`, `one_gigabyte`      | bytes     | Binary (×1024 per step)   |
| **count**  | `count`, `one_thousand`, `one_million`                          | 1         | ×1, ×1,000, ×1,000,000    |

**Cross-group conversion is not allowed.** Providing time usage with data pricing (or any other mismatch) raises a `ValueError`.

**Example — graduated pricing in minutes, usage in hours:**

```json
{
    "type": "graduated",
    "based_on": "one_minute",
    "tiers": [
        { "up_to": 60, "unit_price": "0" },
        { "up_to": null, "unit_price": "0.10" }
    ]
}
```

With `UsageData(one_hour=2)`: 2 hours = 120 minutes. First 60 free, next 60 at $0.10 = $6.00.

---

## Volume Pricing Types

These pricing types are designed for `payout_price` to handle volume-based billing over a billing period. They use aggregate metrics like `request_count` (total requests in billing period) or combine multiple pricing components.

> **Note:** While `add` and `multiply` can technically be used for `list_price` when wrapping per-request types, `tiered` and `graduated` with `based_on: "request_count"` are seller-only.

**Additional metrics available for volume pricing:**

| Metric          | Description                              | Availability |
| --------------- | ---------------------------------------- | ------------ |
| `request_count` | Number of API requests in billing period | Seller only  |

### Constant Pricing (`constant`) - Billing Period

When used in volume pricing contexts (e.g., inside `tiered` tiers or combined with `add`), `constant` represents a fixed amount for the billing period rather than per request.

**Example - Flat monthly fee based on tier:**

```json
{
    "type": "tiered",
    "based_on": "request_count",
    "tiers": [
        { "up_to": 1000, "price": { "type": "constant", "price": "10.00" } },
        { "up_to": 10000, "price": { "type": "constant", "price": "50.00" } },
        { "up_to": null, "price": { "type": "constant", "price": "200.00" } }
    ],
    "description": "Flat monthly fee based on request volume"
}
```

### Add Pricing (`add`)

Combines multiple pricing components by summing them together. Useful for base price + fees, or combining different pricing models.

**Fields:**

| Field    | Type   | Required | Description                             |
| -------- | ------ | -------- | --------------------------------------- |
| `type`   | string | **Yes**  | Must be `"add"`                         |
| `prices` | array  | **Yes**  | List of pricing objects to sum together |

**Example - Token pricing with per-request fee:**

```json
{
    "type": "add",
    "prices": [
        { "type": "one_million_tokens", "input": "0.50", "output": "1.50" },
        {
            "type": "constant",
            "price": "0.001",
            "description": "Per-request fee"
        }
    ]
}
```

**Example - Graduated pricing for both input and output tokens:**

```json
{
    "type": "add",
    "prices": [
        {
            "type": "graduated",
            "based_on": "input_tokens",
            "tiers": [
                { "up_to": 1000000, "unit_price": "0.000001" },
                { "up_to": null, "unit_price": "0.0000005" }
            ]
        },
        {
            "type": "graduated",
            "based_on": "output_tokens",
            "tiers": [
                { "up_to": 1000000, "unit_price": "0.000003" },
                { "up_to": null, "unit_price": "0.0000015" }
            ]
        }
    ],
    "description": "Graduated token pricing with separate input/output rates"
}
```

### Multiply Pricing (`multiply`)

Applies a multiplier to a base pricing model. Useful for percentage-based adjustments.

**Fields:**

| Field    | Type   | Required | Description                                  |
| -------- | ------ | -------- | -------------------------------------------- |
| `type`   | string | **Yes**  | Must be `"multiply"`                         |
| `factor` | string | **Yes**  | Multiplication factor (e.g., "0.70" for 70%) |
| `base`   | object | **Yes**  | Base pricing object to multiply              |

**Example - 70% of standard pricing:**

```json
{
    "type": "multiply",
    "factor": "0.70",
    "base": { "type": "one_million_tokens", "input": "1.00", "output": "2.00" },
    "description": "Partner discount (30% off)"
}
```

### Max Pricing (`max`)

Charges the **highest** cost among multiple pricing calculations. Useful for "charge by count OR by duration, whichever is higher" patterns.

**Lenient:** Children that can't process the usage (e.g., missing metric) are silently skipped. At least one child must succeed.

**Fields:**

| Field    | Type   | Required | Description                                         |
| -------- | ------ | -------- | --------------------------------------------------- |
| `type`   | string | **Yes**  | Must be `"max"`                                     |
| `prices` | array  | **Yes**  | List of pricing objects — the highest result is used |

**Example — charge per-count OR per-duration, whichever is higher:**

```json
{
    "type": "max",
    "prices": [
        { "type": "image", "price": "0.05" },
        { "type": "one_second", "price": "0.01" }
    ],
    "description": "Higher of per-image or per-second charge"
}
```

### Min Pricing (`min`)

Charges the **lowest** cost among multiple pricing calculations. Useful for price caps — usage-based pricing but never more than a flat rate.

**Lenient:** Children that can't process the usage are silently skipped.

**Fields:**

| Field    | Type   | Required | Description                                        |
| -------- | ------ | -------- | -------------------------------------------------- |
| `type`   | string | **Yes**  | Must be `"min"`                                    |
| `prices` | array  | **Yes**  | List of pricing objects — the lowest result is used |

**Example — usage-based pricing capped at $100:**

```json
{
    "type": "min",
    "prices": [
        { "type": "one_second", "price": "0.10" },
        { "type": "constant", "price": "100.00" }
    ],
    "description": "Per-second pricing capped at $100"
}
```

### First Pricing (`first`)

Returns the cost from the **first** child pricing that can handle the usage. Tries each child in order; the first one that succeeds wins.

**Lenient:** Children that raise errors are skipped until one succeeds.

Useful when pricing should adapt to whatever metric the caller provides (duration OR count, etc.).

**Fields:**

| Field    | Type   | Required | Description                                                  |
| -------- | ------ | -------- | ------------------------------------------------------------ |
| `type`   | string | **Yes**  | Must be `"first"`                                            |
| `prices` | array  | **Yes**  | List of pricing objects — the first successful result is used |

**Example — charge by duration if available, otherwise by count:**

```json
{
    "type": "first",
    "prices": [
        { "type": "one_second", "price": "0.01" },
        { "type": "image", "price": "0.05" }
    ],
    "description": "Duration-based if available, otherwise per-image"
}
```

### Tiered Pricing (`tiered`)

Volume-based pricing where the tier determines the price for ALL usage. Once you cross a threshold, all units are priced at that tier's rate.

**Fields:**

| Field      | Type   | Required | Description                              |
| ---------- | ------ | -------- | ---------------------------------------- |
| `type`     | string | **Yes**  | Must be `"tiered"`                       |
| `based_on` | string | **Yes**  | Metric for tier selection                |
| `tiers`    | array  | **Yes**  | List of tier objects, ordered by `up_to` |

**Tier Object:**

| Field   | Type    | Required | Description                                      |
| ------- | ------- | -------- | ------------------------------------------------ |
| `up_to` | integer | **Yes**  | Upper limit for this tier (`null` for unlimited) |
| `price` | object  | **Yes**  | Pricing object for this tier                     |

**Example - Fixed price tiers based on request volume:**

```json
{
    "type": "tiered",
    "based_on": "request_count",
    "tiers": [
        { "up_to": 1000, "price": { "type": "constant", "price": "10.00" } },
        { "up_to": 10000, "price": { "type": "constant", "price": "80.00" } },
        { "up_to": null, "price": { "type": "constant", "price": "500.00" } }
    ],
    "description": "Volume-based flat pricing"
}
```

**How it works:**

- 500 requests → Tier 1 → $10.00
- 5,000 requests → Tier 2 → $80.00
- 50,000 requests → Tier 3 → $500.00

**Example - Different token rates based on request volume:**

```json
{
    "type": "tiered",
    "based_on": "request_count",
    "tiers": [
        {
            "up_to": 1000,
            "price": {
                "type": "one_million_tokens",
                "input": "3.00",
                "output": "15.00"
            }
        },
        {
            "up_to": null,
            "price": {
                "type": "one_million_tokens",
                "input": "1.50",
                "output": "7.50"
            }
        }
    ],
    "description": "Volume discount on token pricing"
}
```

### Graduated Pricing (`graduated`)

AWS-style pricing where each tier's units are priced at that tier's rate. You always pay the higher rate for the first N units, regardless of total volume.

**Fields:**

| Field      | Type   | Required | Description                              |
| ---------- | ------ | -------- | ---------------------------------------- |
| `type`     | string | **Yes**  | Must be `"graduated"`                    |
| `based_on` | string | **Yes**  | Metric for tier calculation              |
| `tiers`    | array  | **Yes**  | List of tier objects, ordered by `up_to` |

**Graduated Tier Object:**

| Field        | Type    | Required | Description                                      |
| ------------ | ------- | -------- | ------------------------------------------------ |
| `up_to`      | integer | **Yes**  | Upper limit for this tier (`null` for unlimited) |
| `unit_price` | string  | **Yes**  | Price per unit in this tier                      |

**Example - Per-request graduated pricing:**

```json
{
    "type": "graduated",
    "based_on": "request_count",
    "tiers": [
        { "up_to": 1000, "unit_price": "0.01" },
        { "up_to": 10000, "unit_price": "0.008" },
        { "up_to": null, "unit_price": "0.005" }
    ],
    "description": "Graduated per-request pricing"
}
```

**How it works (5,000 requests):**

- First 1,000 × $0.01 = $10.00
- Next 4,000 × $0.008 = $32.00
- **Total = $42.00**

**Example - First 1 million requests free, then pay per request:**

```json
{
    "type": "graduated",
    "based_on": "request_count",
    "tiers": [
        { "up_to": 1000000, "unit_price": "0" },
        { "up_to": null, "unit_price": "0.00001" }
    ],
    "description": "First 1M requests free, then $0.00001 per request"
}
```

### Tiered vs Graduated: Key Difference

| Model         | 5,000 requests                    | Result     |
| ------------- | --------------------------------- | ---------- |
| **Tiered**    | All 5,000 at tier 2 rate ($0.008) | **$40.00** |
| **Graduated** | 1,000 × $0.01 + 4,000 × $0.008    | **$42.00** |

- **Tiered (Volume)**: Rewards high volume - once you reach a tier, ALL units get that rate
- **Graduated**: Each portion pays its tier's rate - first units always cost more

### Expression-Based `based_on`

Both `tiered` and `graduated` pricing support arithmetic expressions in the `based_on` field, enabling complex tier selection logic based on computed values rather than single metrics.

**Supported Operations:**

| Operation      | Example                              | Description                     |
| -------------- | ------------------------------------ | ------------------------------- |
| Addition       | `input_tokens + output_tokens`       | Sum of two metrics              |
| Subtraction    | `total_tokens - input_tokens`        | Difference between metrics      |
| Multiplication | `output_tokens * 4`                  | Metric multiplied by a factor   |
| Division       | `input_tokens / 1000`                | Metric divided by a factor      |
| Parentheses    | `(input_tokens + output_tokens) * 2` | Group operations for precedence |
| Unary minus    | `input_tokens - -100`                | Negation                        |

**Example - Weighted Token Pricing (output tokens cost 4x more):**

```json
{
    "type": "tiered",
    "based_on": "input_tokens + output_tokens * 4",
    "tiers": [
        { "up_to": 10000, "price": { "type": "constant", "price": "1.00" } },
        { "up_to": null, "price": { "type": "constant", "price": "10.00" } }
    ],
    "description": "Higher tier when weighted token usage exceeds 10k"
}
```

How it works:

- 5000 input + 1000 output → 5000 + 4000 = 9000 → Tier 1 ($1.00)
- 5000 input + 2000 output → 5000 + 8000 = 13000 → Tier 2 ($10.00)

**Example - Combine Request Count and Token Usage:**

```json
{
    "type": "tiered",
    "based_on": "request_count * 100 + input_tokens",
    "tiers": [
        { "up_to": 10000, "price": { "type": "constant", "price": "1.00" } },
        { "up_to": null, "price": { "type": "constant", "price": "5.00" } }
    ],
    "description": "Tier based on weighted combination of requests and tokens"
}
```

**Error Handling:**

Invalid expressions will raise errors at calculation time:

- **Invalid syntax**: `"input_tokens +"` → `Invalid expression syntax`
- **Unknown metric**: `"input_tokens + unknown_field"` → `Unknown metric: unknown_field`
- **Unsupported operator**: `"input_tokens ** 2"` → `Unsupported operator: Pow`

---

## Seller-Only Pricing Types

These pricing types use `customer_charge`, which is only available for `payout_price` calculations. This metric represents what the customer was charged and is used for revenue-sharing arrangements.

> **Important:** These pricing types should **only** be used for `payout_price`. Using them for `list_price` will result in errors or undefined behavior.

**Additional metrics available for seller pricing:**

| Metric            | Description                          | Availability |
| ----------------- | ------------------------------------ | ------------ |
| `customer_charge` | Total amount charged to the customer | Seller only  |

### Revenue Share Pricing (`revenue_share`)

For revenue-sharing arrangements where the seller receives a percentage of the customer charge.

**Fields:**

| Field        | Type   | Required | Description                                          |
| ------------ | ------ | -------- | ---------------------------------------------------- |
| `type`       | string | **Yes**  | Must be `"revenue_share"`                            |
| `percentage` | string | **Yes**  | Percentage of customer charge for the seller (0-100) |

**How it works:**

The `percentage` field represents the seller's share of whatever the customer pays. For example:

- If `percentage` is `"70"` and the customer pays $10, the seller receives $7
- If `percentage` is `"85.5"` and the customer pays $100, the seller receives $85.50

**Example:**

```json
{
    "type": "revenue_share",
    "percentage": "70.00",
    "description": "70% revenue share"
}
```

**TOML Example:**

```toml
[payout_price]
type = "revenue_share"
percentage = "70.00"
description = "70% revenue share"
```

**Use Cases:**

- Marketplace arrangements where sellers want a fixed percentage rather than per-unit pricing
- Reseller agreements with variable customer pricing
- Partner programs with revenue-sharing terms

### Expression Pricing (`expr`)

Expression-based pricing that evaluates an arbitrary arithmetic expression using usage metrics. This is useful when the upstream provider's pricing involves complex calculations that can't be expressed with basic pricing types.

**Fields:**

| Field  | Type   | Required | Description                               |
| ------ | ------ | -------- | ----------------------------------------- |
| `type` | string | **Yes**  | Must be `"expr"`                          |
| `expr` | string | **Yes**  | Arithmetic expression using usage metrics |

**Available Metrics:**

- `input_tokens`, `output_tokens`, `total_tokens` - Token counts
- `seconds` - Time-based usage
- `count` - Generic count (images, steps, etc.)
- `request_count` - Number of API requests (seller only)
- `customer_charge` - What the customer paid (seller only)

**Supported Operations:**

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Parentheses: `(` `)`
- Numeric literals: `1000000`, `0.5`, etc.

**Example - Token Pricing with Different Rates:**

```json
{
    "type": "expr",
    "expr": "input_tokens / 1000000 * 0.50 + output_tokens / 1000000 * 1.50",
    "description": "Custom token pricing"
}
```

**Example - Complex Weighted Pricing:**

```json
{
    "type": "expr",
    "expr": "(input_tokens + output_tokens * 4) / 1000000 * 2.00",
    "description": "Output tokens weighted 4x"
}
```

**Example - Revenue Share as Expression:**

```json
{
    "type": "expr",
    "expr": "customer_charge * 0.70",
    "description": "70% revenue share"
}
```

**Example - Per-Request Fee:**

```json
{
    "type": "expr",
    "expr": "request_count * 0.001 + input_tokens / 1000000 * 0.50",
    "description": "Per-request fee plus token cost"
}
```

**TOML Example:**

```toml
[payout_price]
type = "expr"
expr = "input_tokens / 1000000 * 0.50 + output_tokens / 1000000 * 1.50"
description = "Custom token pricing for seller"
```

---

## Nested Composite Pricing

Composite pricing types can be nested for complex scenarios:

**Example - Graduated pricing with minimum fee:**

```json
{
    "type": "add",
    "prices": [
        {
            "type": "graduated",
            "based_on": "request_count",
            "tiers": [
                { "up_to": 1000, "unit_price": "0.01" },
                { "up_to": null, "unit_price": "0.005" }
            ]
        },
        {
            "type": "constant",
            "price": "5.00",
            "description": "Minimum monthly fee"
        }
    ]
}
```

**Example - Tiered pricing with partner discount:**

```json
{
    "type": "multiply",
    "factor": "0.80",
    "base": {
        "type": "tiered",
        "based_on": "request_count",
        "tiers": [
            {
                "up_to": 10000,
                "price": {
                    "type": "one_million_tokens",
                    "input": "1.00",
                    "output": "2.00"
                }
            },
            {
                "up_to": null,
                "price": {
                    "type": "one_million_tokens",
                    "input": "0.50",
                    "output": "1.00"
                }
            }
        ]
    },
    "description": "Partner pricing (20% discount on tiered rates)"
}
```

---

## Complete Examples

### Service File with Seller Price (JSON)

```json
{
    "schema": "offering_v1",
    "name": "gpt-4-turbo",
    "display_name": "GPT-4 Turbo",
    "description": "OpenAI's most advanced model",
    "service_type": "llm",
    "currency": "USD",
    "time_created": "2024-01-15T10:00:00Z",
    "details": {
        "context_window": 128000,
        "max_output_tokens": 4096
    },
    "upstream_access_config": {
        "OpenAI Chat API": {
            "access_method": "http",
            "base_url": "https://api.openai.com/v1/chat/completions"
        }
    },
    "payout_price": {
        "type": "one_million_tokens",
        "input": "10.00",
        "output": "30.00",
        "description": "OpenAI GPT-4 Turbo pricing",
        "reference": "https://openai.com/pricing"
    }
}
```

### Service File with Seller Price (TOML)

```toml
schema = "offering_v1"
name = "whisper-large"
display_name = "Whisper Large V3"
description = "Audio transcription model"
service_type = "audio_transcription"
currency = "USD"
time_created = "2024-01-15T10:00:00Z"

[upstream_access_config."OpenAI Audio API"]
access_method = "http"
base_url = "https://api.openai.com/v1/audio/transcriptions"

[payout_price]
type = "one_second"
price = "0.006"
description = "Per second of audio"
reference = "https://openai.com/pricing"
```

### Listing File with Customer Price (TOML)

```toml
schema = "listing_v1"
name = "gpt-4-turbo-premium-usd"
service_name = "gpt-4-turbo"
display_name = "GPT-4 Turbo Premium Access"
status = "ready"
currency = "USD"
time_created = "2024-02-01T12:00:00Z"

[[user_access_interfaces]]
access_method = "http"
base_url = "${API_GATEWAY_BASE_URL}/v1/chat/completions"
name = "Chat Completions API"

[user_access_interfaces.routing_key]
model = "gpt-4-turbo"

[list_price]
type = "one_million_tokens"
input = "12.00"
output = "36.00"
description = "Premium access with priority support"
```

### Image Generation Service (JSON)

```json
{
    "schema": "offering_v1",
    "name": "flux-pro",
    "display_name": "FLUX Pro",
    "description": "High-quality image generation",
    "service_type": "image_generation",
    "currency": "USD",
    "time_created": "2024-03-15T10:30:00Z",
    "details": {
        "max_resolution": "2048x2048",
        "supported_formats": ["PNG", "JPEG", "WEBP"]
    },
    "upstream_access_config": {
        "Image Generation API": {
            "access_method": "http",
            "base_url": "https://api.provider.com/v1/images/generate"
        }
    },
    "payout_price": {
        "type": "image",
        "price": "0.04",
        "description": "Per image pricing"
    }
}
```

---

## Pricing Type Selection Guide

### Per-Request Pricing Types (for `list_price` and `payout_price`)

| Service Type                | Recommended Pricing Type | Example Use Cases              |
| --------------------------- | ------------------------ | ------------------------------ |
| LLM, Chat, Completion       | `one_million_tokens`     | GPT-4, Claude, Llama           |
| Embedding                   | `one_million_tokens`     | text-embedding-ada-002         |
| Cheap token services        | `one_thousand_tokens`    | Lightweight models             |
| Audio Transcription         | `one_second`             | Whisper, Deepgram              |
| Text-to-Speech              | `one_second`             | ElevenLabs, Azure TTS          |
| Video Processing            | `one_second`             | Video transcription, analysis  |
| Alias / subscription        | `one_month`              | URL aliases, reserved slots    |
| Image Generation            | `image`                  | DALL-E, Stable Diffusion, FLUX |
| Image Analysis              | `image`                  | GPT-4 Vision (per image)       |
| Diffusion with Step Control | `step`                   | Custom diffusion pipelines     |
| Data transfer / storage     | `one_gigabyte`           | CDN, object storage            |
| High-volume API calls       | `one_thousand`           | Logging, analytics events      |
| Per-request fees/discounts  | `constant`               | Fixed fee per API request      |

### Volume Pricing Types (for `payout_price` - uses `request_count`)

| Use Case                | Recommended Type | Description                          |
| ----------------------- | ---------------- | ------------------------------------ |
| Flat billing period fee | `constant`       | Fixed amount per billing period      |
| Combined pricing        | `add`            | Sum of multiple pricing components   |
| Percentage adjustments  | `multiply`       | Apply discount/markup factor         |
| Charge the higher of    | `max`            | Highest of multiple calculations     |
| Price cap               | `min`            | Lowest of multiple (cap at flat fee) |
| Flexible metric         | `first`          | Use whichever metric is available    |
| Request-based tiers     | `tiered`         | Tiers based on `request_count`       |
| Request-based graduated | `graduated`      | Graduated pricing by `request_count` |

### Seller-Only Pricing Types (for `payout_price` - uses `customer_charge`)

| Use Case            | Recommended Type | Description                      |
| ------------------- | ---------------- | -------------------------------- |
| Revenue sharing     | `revenue_share`  | Percentage of customer charge    |
| Complex expressions | `expr`           | Arbitrary arithmetic expressions |

---

## Validation

When you run `usvc_seller data validate`, the pricing structure is validated:

1. **JSON Schema Validation**: Ensures the structure matches the expected format
2. **Pydantic Model Validation**: Enforces business rules:
    - `type` must be a valid pricing type
    - Token pricing requires either `price` (unified) or both `input`/`output` (separate)
    - When `input`/`output` are set without `price`, `price` is auto-computed
    - Negative values are allowed (for seller-funded incentives via `payout_price`)
    - Extra fields are rejected

### Common Validation Errors

**Invalid: Missing output price**

```json
{
    "type": "one_million_tokens",
    "input": "0.50"
}
```

Error: "Both 'input' and 'output' must be specified for separate pricing"

**Invalid: Unknown pricing type**

```json
{
    "type": "per_request",
    "price": "0.001"
}
```

Error: "Invalid pricing type. Valid types: 'one_million_tokens', 'one_thousand_tokens', 'one_token', 'one_second', 'one_minute', 'one_hour', 'one_day', 'one_month', 'one_byte', 'one_kilobyte', 'one_megabyte', 'one_gigabyte', 'one_thousand', 'one_million', 'image', 'step', 'revenue_share', 'constant', 'add', 'multiply', 'tiered', 'graduated', 'expr'"

---

## Cost Calculation

The backend calculates costs using these formulas:

### Per-Request Pricing Types

| Pricing Type                   | Cost Formula                                                            |
| ------------------------------ | ----------------------------------------------------------------------- |
| `one_million_tokens` (separate) | (input_tokens × input + cached_input_tokens × cached_input + output_tokens × output) / 1,000,000 |
| `one_million_tokens` (unified)  | total_tokens × price / 1,000,000                                        |
| `one_thousand_tokens`          | Same as above with divisor 1,000                                        |
| `one_token`                    | Same as above with divisor 1                                            |
| `one_second` / `one_minute` / `one_hour` / `one_day` / `one_month` | usage (converted to pricing unit) × price |
| `one_byte` / `one_kilobyte` / `one_megabyte` / `one_gigabyte` | usage (converted to pricing unit) × price |
| `one_thousand` / `one_million` | usage (converted to pricing unit) × price                               |
| `image`                        | count × price                                                           |
| `step`                         | count × price                                                           |
| `constant`                     | amount (fixed value per request)                                        |

### Volume Pricing Types

| Pricing Type | Cost Formula                                                       |
| ------------ | ------------------------------------------------------------------ |
| `constant`   | amount (fixed value per billing period)                            |
| `add`        | sum(price.calculate_cost() for each price in prices)               |
| `multiply`   | base.calculate_cost() × factor                                     |
| `max`        | max(price.calculate_cost() for each applicable price)              |
| `min`        | min(price.calculate_cost() for each applicable price)              |
| `first`      | First price.calculate_cost() that succeeds                         |
| `tiered`     | Find tier where metric ≤ up_to, return tier.price.calculate_cost() |
| `graduated`  | Sum of (units_in_tier × unit_price) for each tier                  |

### Seller-Only Pricing Types

| Pricing Type    | Cost Formula                           |
| --------------- | -------------------------------------- |
| `revenue_share` | customer_charge × percentage / 100     |
| `expr`          | Evaluate expression with usage metrics |

---

## See Also

- [File Schemas](file-schemas.md) - Complete schema reference
- [Data Structure](data-structure.md) - File organization
- [CLI Reference](cli-reference.md#usvc_seller-data-validate-validate-data) - Validation command
