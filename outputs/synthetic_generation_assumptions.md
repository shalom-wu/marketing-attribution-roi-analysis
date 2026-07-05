# Synthetic Data Generation Assumptions

This dataset is synthetic. It is not customer data and should not be represented as real marketing performance.

| Field | Assumption |
|---|---|
| Dataset type | synthetic |
| Journey count | 15,000 |
| Period | 2026-01-01 to 2026-03-31 |
| Random seed | 42 |
| Grain | one row per customer journey touchpoint |
| Business context | mid-size e-commerce business; no fabricated brand name or real customer data |

## Modeling Logic

- Synthetic conversion probability is a logistic-style function of channel presence, journey length, lower-funnel final touches, and upper-plus-lower-funnel synergy.
- Converted journeys receive capped lognormal synthetic order revenue.
- Channels included: Display, Paid Social, Referral, Organic Search, Paid Search, Affiliate, Email, Direct.

The synthetic setup intentionally creates a common attribution problem: lower-funnel channels such as Paid Search, Email, and Direct often appear late in journeys, while awareness and consideration channels help create demand earlier in the path. This lets the project demonstrate why last-touch attribution can misallocate budget.
