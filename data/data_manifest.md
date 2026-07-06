# Data Manifest

This repo includes the source shard used for preparation, the processed project sample, and the exact Power BI-ready outputs.

| File | Type | Shape / size | Used by | Notes |
|---|---|---:|---|---|
| `raw/criteo_day1_part-00238.parquet` | Real source shard | 310,766 x 150, 97.4 MB | Source prep, audit | CriteoPrivateAd shard from Hugging Face; card checked 2026-07-06; license `cc-by-sa-4.0`. |
| `processed/criteo_touchpoints_sample.csv` | Derived project sample | 24,075 x 16, 4.5 MB | Python, SQL, tests, Power BI | Touchpoint-level sample with anonymized publisher groups and assumed contribution value. |
| `powerbi/fact_touchpoints.csv` | Derived | 24,075 x 16, 4.5 MB | Power BI | Same project sample exported by SQL. |
| `powerbi/fact_journey_summary.csv` | Derived | 11,343 x 10, 2.0 MB | Power BI | One row per journey with path and conversion fields. |
| `powerbi/kpi_touchpoint_summary.csv` | Derived aggregate | 9 x 6, <1 KB | Power BI | Channel touchpoints, journey coverage, and conversion rate when seen. |
| `powerbi/kpi_attribution_summary.csv` | Derived model output | 36 x 4, 2.0 KB | Power BI | First-touch, last-touch, linear, and Markov-removal credit shares. |
| `powerbi/budget_reallocation.csv` | Derived + assumed | 9 x 10, 1.7 KB | Power BI | Recommended budget shift from current assumed pilot budget toward Markov-removal credit. |
| `powerbi/scenario_summary.csv` | Derived + assumed | 3 x 9, <1 KB | Power BI | Conservative, balanced, and aggressive budget scenarios. |
| `powerbi/journey_patterns.csv` | Derived aggregate | 12 x 4, <1 KB | Power BI | Most common path patterns. |

Budget and revenue fields are not observed in the source dataset; they are explicit modeling assumptions. The attribution results should be described as decision-support and not causal incrementality.
