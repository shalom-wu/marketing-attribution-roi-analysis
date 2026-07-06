# SQL Layer - Attribution Validation and Budget KPIs

This folder adds a DuckDB validation and aggregation layer on top of the included Criteo-derived project sample and the Python attribution outputs.

Run it from the project root:

```bash
python scripts/run_sql.py
```

Files run in order:

| File | Purpose |
|---|---|
| `create_tables.sql` | Creates views over the included touchpoint sample and journey summary. |
| `data_quality_checks.sql` | Checks journey counts, duplicate touchpoint IDs, channel coverage, and source framing. |
| `kpi_views.sql` | Defines channel funnel, attribution, budget, scenario, and journey-pattern views. |
| `analysis_queries.sql` | Prints the channel and budget cuts a reviewer should inspect first. |

Exports written to `data/powerbi/`:

- `fact_touchpoints.csv`
- `fact_journey_summary.csv`
- `kpi_touchpoint_summary.csv`
- `kpi_attribution_summary.csv`
- `budget_reallocation.csv`
- `scenario_summary.csv`
- `journey_patterns.csv`
