# Marketing Channel Attribution & Budget ROI Analysis

Portfolio project by Shalom Wu (GitHub: @shalom-wu)

I built this project around a common marketing problem: last-touch attribution is easy to explain, but it can quietly distort budget decisions. If the final touchpoint gets all the credit, teams can overfund what closes the journey and underfund what helped create it.

The goal here is not to make attribution look more complicated than it needs to be. The goal is to show how the choice of attribution method changes the budget conversation.

## Data

The analysis uses [CriteoPrivateAd](https://huggingface.co/datasets/criteo/CriteoPrivateAd), a public anonymized advertising dataset hosted by Criteo on Hugging Face. I use one processed sample from `day_int=1`, Parquet shard `part-00238`.

The source data includes real anonymized display-ad impressions, user IDs, campaign IDs, publisher IDs, click labels, and sales labels. It does not include friendly channel names, true calendar dates, advertiser revenue, or a real media budget. Because of that, I label the top publisher placements as `Publisher 01` through `Publisher 08`, group the rest as `Long-tail placements`, and keep the dollar layer clearly assumption-based.

In plain terms: the journeys and conversions are sourced from Criteo. The budget and contribution dollars are modeling assumptions.

## What I Found

The processed sample contains **24,075 touchpoints** across **11,343 multi-touch journeys**. Journey conversion rate is **1.8%**, and the average journey has **2.12 touches**.

Last-touch and Markov attribution are close on the biggest bucket, but they disagree meaningfully on smaller placement groups. `Publisher 03` gets **3.8%** credit under last-touch and **5.6%** under Markov removal. `Publisher 04` moves the other way: **7.3%** under last-touch and **4.1%** under Markov.

Using last-touch as the budget guide would misdirect an estimated **$8.1K**, or **4.7%** of the assumed pilot budget, compared with the Markov-informed allocation. My recommended scenario is a balanced move: shift **$33.3K** toward the Markov mix, with an estimated **$6.5K assumed contribution lift**, then validate before scaling.

## Why This Matters

A lot of attribution projects stop once they produce a model output. I wanted this one to go one step further: what would a marketing team actually do differently on Monday morning?

My answer is not "throw away last-touch." Last-touch is still useful as a simple operational view. I would not use it as the main budget allocator, though. For budget decisions, the Markov model gives a better read on how placements work together across the path.

## Method

1. Download and prepare a CriteoPrivateAd Parquet shard.
2. Keep users with at least two impressions, so the analysis is genuinely multi-touch.
3. Turn each impression into a touchpoint row.
4. Compare first-touch, last-touch, linear, and Markov removal attribution.
5. Translate the attribution results into budget scenarios using explicit spend and contribution assumptions.

## Repo Map

| Path | What to look for |
|---|---|
| `data-sources.md` | Where the data came from and how I transformed it |
| `data/processed/criteo_touchpoints_sample.csv` | The processed Criteo sample used in the analysis |
| `src/attribution_roi/` | Source prep, attribution logic, budget logic, and charting |
| `scripts/` | Rebuild scripts |
| `outputs/` | Generated tables |
| `reports/` | Summary report, markdown deck, and visuals |
| `notebooks/` | Notebook companion |
| `tests/` | Unit tests for source prep, attribution, and budget calculations |

## Run It

Use the committed processed sample:

```bash
pip install -r requirements.txt
python scripts/run_all.py
pytest
```

Or re-download the Criteo shard first:

```bash
pip install -r requirements.txt
python scripts/download_source_data.py
python scripts/run_all.py
pytest
```

The raw Parquet shard and processed project sample are included, so a reviewer
can inspect and run the project without downloading Criteo data first.

## SQL and Power BI layer

The [sql/](sql) folder adds DuckDB validation and KPI views over the included
touchpoint sample and attribution outputs. It checks journey count, channel
coverage, duplicate touchpoint IDs, converted journeys, and source framing.

```bash
python scripts/run_sql.py
```

The runner exports Power BI-ready files to `data/powerbi/`: touchpoints,
journey summary, channel funnel, attribution summary, budget reallocation,
scenario summary, and journey patterns. The [power-bi/](power-bi) folder
contains the dashboard brief, data model, DAX, refresh instructions, manual
build guide, and mockups. No `.pbix` is included yet; I did not create a
placeholder file.

## Main Outputs

- Strategy deck: `reports/strategy_deck.md`
- Executive report: `reports/summary.md`
- Attribution table: `outputs/attribution_summary.csv`
- Budget scenarios: `outputs/scenario_summary.csv`

## Portfolio Use

**CV bullets**

- Built a multi-touch marketing attribution analysis from an anonymized Criteo
  ad-event shard, converting user paths into channel credit and budget
  scenarios.
- Compared first-touch, last-touch, linear, and Markov-removal attribution and
  translated differences into a transparent budget-reallocation framework.
- SQL-focused: Added DuckDB validation and KPI exports for channel funnel,
  attribution method gaps, budget deltas, scenarios, and journey patterns.
- Power BI-focused: Prepared a three-page attribution and budget dashboard
  build spec with dashboard-ready CSV inputs.

**LinkedIn description**

> Marketing Channel Attribution & ROI - I built this project to show how
> attribution changes the budget conversation. The source is CriteoPrivateAd on
> Hugging Face; Python prepares journeys and attribution models, SQL validates
> the channel and journey cuts, and Power BI is documented as the stakeholder
> layer for scenario review.

**Interview explanation**

> "Attribution is not causality, so I framed this as a decision-support model.
> SQL checks the channel and journey tables, Python handles the Markov-removal
> and budget math, and Power BI turns it into a scenario conversation a
> marketing team could critique."

**Likely interview questions**

1. *Why not use last-touch?* Last-touch is easy but often overcredits channels
   near conversion.
2. *Can this prove ROI?* No. It allocates credit; I would test incrementality
   with geo holdouts or randomized experiments.
3. *What is assumed?* Budget and contribution per sale, because the source has
   ad-event labels rather than advertiser finance data.

## Limits I Would Call Out In An Interview

- Criteo anonymizes the source data, so the analysis is about publisher placement groups, not named channels like Search, Social, or Email.
- Dates are relative `day_int` partitions, not real calendar dates.
- The repo uses one shard and multi-touch users from that shard, not the full CriteoPrivateAd dataset.
- Attribution is correlational. It allocates credit across observed paths, but it does not prove incrementality.
- The ROI layer uses assumed spend and assumed contribution per sale because the source data does not include advertiser budget or revenue.

## License

MIT License. Copyright (c) 2026 Shalom Wu.
