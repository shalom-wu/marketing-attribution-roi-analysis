# Data Quality Report

This project uses a deterministic synthetic marketing attribution dataset generated inside the repository.

| Check | Result |
|---|---:|
| Touchpoint rows | 47,308 |
| Customer journeys | 15,000 |
| Converted journeys | 1,898 |
| Journey conversion rate | 12.7% |
| Duplicate touchpoint IDs | 0 |
| Invalid channels | None |
| Date range | 2026-01-01 to 2026-04-07 |

Null counts shown below are expected for `conversion_date`, because non-converting journeys do not have a conversion date.

```json
{
  "conversion_date": 40186
}
```
