# Marketing Attribution And Budget ROI

This repository compares attribution methods on a sourced CriteoPrivateAd sample and shows how attribution choice changes a budget allocation scenario.

The source data contains anonymized publisher placements rather than friendly marketing-channel names. Spend and contribution values are explicit modeling assumptions because the dataset does not include advertiser budget or revenue.

## Project Summary

| Area | Details |
|---|---|
| Business question | How much can attribution method choice change a media budget recommendation? |
| Data | Public CriteoPrivateAd sample from Hugging Face, using one processed shard from `day_int=1`. |
| Methods | Multi-touch journey construction, first-touch, last-touch, linear attribution, Markov removal attribution, budget scenario modeling. |
| Main outputs | Strategy deck, summary report, attribution tables, budget scenarios, Power BI-ready exports. |
| Tools | Python, pytest, DuckDB SQL, Power BI build documentation. |

## Key Findings

| # | Finding | Evidence |
|---|---|---|
| 1 | The sample is large enough for a compact multi-touch case. | 24,075 touchpoints across 11,343 multi-touch journeys. |
| 2 | Conversion is sparse. | Journey conversion rate is about 1.8%, and the average journey has 2.12 touches. |
| 3 | Attribution methods agree on the largest bucket but diverge on smaller placements. | Publisher 03 receives 3.8% credit under last-touch versus 5.6% under Markov removal. |
| 4 | Last-touch can misdirect budget. | Last-touch allocation differs from the Markov-informed allocation by about $8.1K, or 4.7% of the assumed pilot budget. |
| 5 | The recommended scenario is a controlled shift, not a full reallocation. | The balanced scenario shifts $33.3K toward the Markov mix and estimates a $6.5K assumed contribution lift before validation. |

![Attribution model comparison](reports/figures/attribution_model_comparison.png)

## Data

The analysis uses [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd), a public anonymized advertising dataset hosted by Criteo on Hugging Face. The project uses one processed sample from `day_int=1`, Parquet shard `part-00238`.

The source data includes anonymized display-ad impressions, user IDs, campaign IDs, publisher IDs, click labels, and sale labels. It does not include named channels, true calendar dates, advertiser revenue, or real media budgets. Source notes are documented in [data-sources.md](data-sources.md).

## Methodology

1. Download and prepare the selected CriteoPrivateAd Parquet shard.
2. Keep users with at least two impressions so the analysis is genuinely multi-touch.
3. Transform impressions into touchpoint rows and journey-level paths.
4. Compare first-touch, last-touch, linear, and Markov removal attribution.
5. Convert attribution shares into budget scenarios using explicit spend and contribution assumptions.

## Repository Contents

| Path | Purpose |
|---|---|
| [data-sources.md](data-sources.md) | Data source, transformation, and caveat notes. |
| [data/](data) | Raw, processed, and Power BI-ready data files. |
| [src/attribution_roi/](src/attribution_roi) | Source prep, attribution logic, budget logic, and charting. |
| [scripts/](scripts) | Download, pipeline, and SQL export scripts. |
| [outputs/](outputs) | Attribution and scenario output tables. |
| [reports/](reports) | Summary report, strategy deck, and figures. |
| [sql/](sql) | DuckDB validation and KPI exports. |
| [power-bi/](power-bi) | Dashboard brief, model notes, DAX, refresh steps, and mockups. |
| [tests/](tests) | Source prep, attribution, and budget tests. |

## Reproduce

Requires Python 3.11+.

```bash
git clone https://github.com/shalom-wu/marketing-attribution-and-roi.git
cd marketing-attribution-and-roi
pip install -r requirements.txt

python scripts/run_all.py
python scripts/run_sql.py
pytest
```

The raw Parquet shard and processed project sample are included, so the project can be reviewed without downloading Criteo data first.

## Reporting Layer

SQL validates journey counts, placement coverage, duplicate touchpoint IDs, converted journeys, and source framing. The SQL runner exports Power BI-ready files to `data/powerbi/`.

The [power-bi/](power-bi) folder contains the dashboard brief, data model, DAX, refresh instructions, manual build guide, and mockups. No placeholder `.pbix` file is included.

## Limitations

- Criteo anonymizes the source data, so the analysis is about publisher placement groups, not named channels like Search, Social, or Email.
- Dates are relative `day_int` partitions, not real calendar dates.
- The repo uses one shard and multi-touch users from that shard, not the full CriteoPrivateAd dataset.
- Attribution is correlational and does not prove incrementality.
- The ROI layer uses assumed spend and contribution because the source data does not include advertiser budget or revenue.

## License And Credit

MIT License. Copyright (c) 2026 Shalom Wu.

Data credit: CriteoPrivateAd dataset by Criteo, hosted on Hugging Face. See [data-sources.md](data-sources.md) for source notes, transformations, and usage caveats.
