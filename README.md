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
| `explainer-guide/` | Plain-English walkthrough |

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

The raw Parquet file is ignored under `data/raw/` because it is about 100 MB.

## Main Outputs

- Strategy deck: `reports/strategy_deck.md`
- Executive report: `reports/summary.md`
- Beginner explainer: `explainer-guide/explain-it-to-me.md`
- Attribution table: `outputs/attribution_summary.csv`
- Budget scenarios: `outputs/scenario_summary.csv`

## Limits I Would Call Out In An Interview

- Criteo anonymizes the source data, so the analysis is about publisher placement groups, not named channels like Search, Social, or Email.
- Dates are relative `day_int` partitions, not real calendar dates.
- The repo uses one shard and multi-touch users from that shard, not the full CriteoPrivateAd dataset.
- Attribution is correlational. It allocates credit across observed paths, but it does not prove incrementality.
- The ROI layer uses assumed spend and assumed contribution per sale because the source data does not include advertiser budget or revenue.

## License

MIT License. Copyright (c) 2026 Shalom Wu.
