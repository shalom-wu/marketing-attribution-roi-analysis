# Marketing Channel Attribution & Budget ROI Analysis

Portfolio project by Shalom Wu (GitHub: @shalom-wu)

This repo analyzes how different attribution methods change marketing budget decisions for a mid-size e-commerce business. The important business point is simple: last-touch attribution is convenient, but it can send money toward the final observed touchpoint while under-crediting earlier touches that helped move the journey forward.

## Data Source

This project now uses a sourced public dataset: [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd), a Criteo-hosted anonymized advertising dataset on Hugging Face.

Important source notes:

- The repo uses one processed sample from `day_int=1`, Parquet shard `part-00238`.
- The source contains real anonymized display-ad impressions, user IDs, campaign IDs, publisher IDs, click labels, and sales labels.
- The source does **not** disclose named marketing channels, actual calendar dates, advertiser revenue, or a real media budget.
- This repo maps the top publisher placements to `Publisher 01` through `Publisher 08` and groups the remaining publishers as `Long-tail placements`.
- `touchpoint_date` is a relative plotting date derived from `day_int=1`, not a real Criteo calendar date.
- Dollarized ROI uses explicit assumptions: an assumed pilot budget and `$120` contribution per sale.

## Key Findings

- **24,075 sourced touchpoints across 11,343 multi-touch journeys** were prepared from the Criteo shard.
- **Journey conversion rate is 1.8%** in the processed multi-touch sample, with **2.12 average touches per journey**.
- **Last-touch and Markov do not tell the same story.** `Publisher 03` receives **3.8%** credit under last-touch vs. **5.6%** under Markov removal, while `Publisher 04` receives **7.3%** under last-touch vs. **4.1%** under Markov.
- **The cost of using last-touch as the budget guide is dollarized with assumptions**, not claimed from source spend data: **$8.1K**, or **4.7%** of the assumed pilot budget, would be misdirected versus the Markov-informed allocation.
- **Recommended approach: balanced reallocation.** Shift **$33.3K** toward the Markov-informed mix for an estimated **$6.5K assumed contribution lift**, then validate with incrementality testing before scaling.

## Why This Matters

Most naive attribution work stops at "which channel gets credit?" This project connects attribution to the actual operating decision: where a marketing team should move budget, and what tradeoff it is accepting. The recommendation is deliberately not "trust the model blindly." It is a staged reallocation with a causal caveat.

## Methodology

1. **Source and prepare data:** download a CriteoPrivateAd Parquet shard, filter to users with at least two impressions, and transform each impression into a touchpoint row.
2. **EDA:** publisher-placement touch frequency, conversion rates by placement exposure, journey length, and common paths.
3. **Naive baselines:** first-touch, last-touch, and linear attribution.
4. **Data-driven attribution:** Markov chain removal-effect attribution, measuring how modeled conversion probability changes when a placement group is removed from the transition graph.
5. **Budget strategy:** compare assumed current budget, last-touch allocation, and Markov-informed allocation; then estimate staged reallocation scenarios with a diminishing-returns response curve.

## Repo Structure

| Path | Purpose |
|---|---|
| `data-sources.md` | Dataset provenance and transformation notes |
| `data/processed/criteo_touchpoints_sample.csv` | Processed sourced Criteo sample used by the project |
| `src/attribution_roi/` | Data preparation, attribution, budget, reporting, and visualization code |
| `scripts/` | One-command scripts for download, analysis, deck, and notebook |
| `outputs/` | Analysis tables and model outputs |
| `reports/` | Executive summary, strategy deck, and presentation visuals |
| `notebooks/` | Reproducible notebook companion |
| `tests/` | Unit tests for source prep, attribution, and budget logic |
| `explainer-guide/` | Plain-English guide for non-technical readers |

## Reproduce The Project

Use the committed processed sample:

```bash
pip install -r requirements.txt
python scripts/run_all.py
pytest
```

Re-download and rebuild the processed sample from Hugging Face:

```bash
pip install -r requirements.txt
python scripts/download_source_data.py
python scripts/run_all.py
pytest
```

The raw Parquet shard is ignored under `data/raw/` because it is about 100 MB.

## Main Outputs

- Strategy deck: `reports/strategy_deck.md`
- Executive report: `reports/summary.md`
- Beginner explainer: `explainer-guide/explain-it-to-me.md`
- Attribution table: `outputs/attribution_summary.csv`
- Budget scenarios: `outputs/scenario_summary.csv`

## Limitations

- **Anonymized source:** CriteoPrivateAd uses anonymized IDs, so the repo analyzes publisher-placement groups rather than human-readable marketing channel names.
- **Relative dates:** the source is partitioned by `day_int`; calendar dates are not disclosed.
- **Sampled scope:** the repo uses one shard and multi-touch users from that shard, not the full 100M-row dataset.
- **Correlational attribution:** Markov removal uses observed journey paths; it does not prove causal incrementality.
- **Dollar assumptions:** source data includes sales labels but not advertiser revenue or budget, so ROI uses explicit assumed contribution and spend.

## License

MIT License. Copyright (c) 2026 Shalom Wu.
