# Data Model

Load these files from `data/powerbi/`:

| Table | File | Grain |
|---|---|---|
| `fact_touchpoints` | `fact_touchpoints.csv` | One row per touchpoint. |
| `fact_journey_summary` | `fact_journey_summary.csv` | One row per journey. |
| `kpi_touchpoint_summary` | `kpi_touchpoint_summary.csv` | One row per channel. |
| `kpi_attribution_summary` | `kpi_attribution_summary.csv` | Method-channel attribution credit. |
| `budget_reallocation` | `budget_reallocation.csv` | One row per channel. |
| `scenario_summary` | `scenario_summary.csv` | One row per reallocation scenario. |
| `journey_patterns` | `journey_patterns.csv` | One row per common path pattern. |

Suggested relationships:

| From | To | Cardinality |
|---|---|---|
| `fact_touchpoints[journey_id]` | `fact_journey_summary[journey_id]` | many-to-one |
| `fact_touchpoints[channel]` | `kpi_touchpoint_summary[channel]` | many-to-one |
| `budget_reallocation[channel]` | `kpi_touchpoint_summary[channel]` | many-to-one |

Keep `kpi_attribution_summary` disconnected if using method slicers; otherwise create a channel dimension table.
