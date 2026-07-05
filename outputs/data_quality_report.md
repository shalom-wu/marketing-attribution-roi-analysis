# Data Quality Check

This is the quick QA pass on the processed CriteoPrivateAd sample used in the project.

| Check | Result |
|---|---:|
| Touchpoint rows | 24,075 |
| Customer journeys | 11,343 |
| Converted journeys | 204 |
| Journey conversion rate | 1.8% |
| Duplicate touchpoint IDs | 0 |
| Invalid channels | None |
| Date range | 2025-01-01 to 2025-01-01 |

The only material null count is `conversion_date`, which is expected because non-converting journeys do not have a conversion date.

```json
{
  "conversion_date": 23635
}
```
