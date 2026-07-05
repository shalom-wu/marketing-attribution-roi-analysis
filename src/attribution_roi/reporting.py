from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def fmt_money(value: float) -> str:
    return f"${value:,.0f}"


def fmt_money_k(value: float) -> str:
    return f"${value / 1000:,.1f}K"


def fmt_pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_data_quality_markdown(path: Path, quality: dict[str, object]) -> None:
    body = f"""# Data Quality Check

This is the quick QA pass on the processed CriteoPrivateAd sample used in the project.

| Check | Result |
|---|---:|
| Touchpoint rows | {quality['rows']:,} |
| Customer journeys | {quality['journeys']:,} |
| Converted journeys | {quality['converted_journeys']:,} |
| Journey conversion rate | {fmt_pct(float(quality['conversion_rate']))} |
| Duplicate touchpoint IDs | {quality['duplicate_touchpoint_ids']:,} |
| Invalid channels | {', '.join(quality['invalid_channels']) if quality['invalid_channels'] else 'None'} |
| Date range | {quality['min_touchpoint_date']} to {quality['max_touchpoint_date']} |

The only material null count is `conversion_date`, which is expected because non-converting journeys do not have a conversion date.

```json
{json.dumps(quality['null_counts'], indent=2)}
```
"""
    path.write_text(body, encoding="utf-8")


def write_source_markdown(path: Path, assumptions: dict[str, object]) -> None:
    body = f"""# Source Data Notes

This sample comes from CriteoPrivateAd, a public anonymized advertising dataset hosted on Hugging Face. I keep the processed sample in the repo and leave the raw Parquet shard out because it is large.

| Field | Assumption |
|---|---|
| Dataset type | {assumptions['dataset_type']} |
| Source | [{assumptions['source_name']}]({assumptions['source_url']}) |
| Source file | {assumptions['source_file_url']} |
| Grain | {assumptions['grain']} |
| Source period | {assumptions['source_period']} |
| Sample filter | {assumptions['sample_filter']} |

## Transformation Notes

- `channel` is an anonymized publisher placement group. The eight highest-volume publishers are labeled `Publisher 01` through `Publisher 08`; everything else is grouped as `Long-tail placements`.
- CriteoPrivateAd uses relative `day_int` partitions, not real calendar dates. I map `day_int=1` to `2025-01-01` only to keep plots and tables readable.
- Contribution value is modeled as `sales_count * $120` because the source provides sales labels, not advertiser revenue.
- Channels included: {', '.join(assumptions['channels'])}.

The source contains real anonymized display-ad impressions, campaign and publisher IDs, click labels, and sales labels. It does not contain named marketing channels, actual calendar dates, advertiser revenue, or a finance-approved media budget.
"""
    path.write_text(body, encoding="utf-8")


def write_summary_report(
    path: Path,
    quality: dict[str, object],
    touch_summary: pd.DataFrame,
    journeys: pd.DataFrame,
    attribution: pd.DataFrame,
    budget: pd.DataFrame,
    scenarios: pd.DataFrame,
    status_quo: dict[str, float],
) -> None:
    markov = attribution.loc[attribution["method"] == "Markov removal"].sort_values("credit_share", ascending=False)
    last = attribution.loc[attribution["method"] == "Last touch"].set_index("channel")
    top_markov = markov.iloc[0]
    increase_gap = budget.sort_values("budget_gap_to_markov", ascending=False).iloc[0]
    reduction_gap = budget.sort_values("budget_gap_to_markov", ascending=True).iloc[0]
    recommended_scenario = scenarios.loc[scenarios["scenario"] == "Balanced reallocation"].iloc[0]
    avg_journey_length = journeys["journey_length"].mean()

    body = f"""# Marketing Attribution & Budget ROI Analysis

## Bottom Line

Last-touch is not wildly wrong in this sample, but it still changes the budget conversation. The top Markov placement, `{top_markov['channel']}`, gets {fmt_pct(top_markov['credit_share'])} of assumed contribution value under Markov and {fmt_pct(float(last.loc[top_markov['channel'], 'credit_share']))} under last-touch.

Using last-touch as the budget guide would move an estimated **{fmt_money_k(status_quo['last_touch_misallocated_budget'])}** of the assumed pilot budget away from the Markov-informed mix. A balanced reallocation estimates **{fmt_money_k(recommended_scenario['estimated_revenue_lift'])}** in assumed contribution lift.

I would treat this as a budget hypothesis, not a final answer. The model uses observed paths, so it is useful for prioritizing where to test, but it does not prove incrementality on its own.

## Dataset Profile

The sample comes from CriteoPrivateAd, a public anonymized advertising dataset hosted on Hugging Face. I use one processed day-one shard and filter to multi-touch users. That leaves **{quality['rows']:,} display touchpoints** across **{quality['journeys']:,} journeys**. Conversion rate is **{fmt_pct(float(quality['conversion_rate']))}**, and the average journey has **{avg_journey_length:.2f} touches**.

Criteo gives relative day partitions rather than real calendar dates, so `2025-01-01` is just a plotting date for `day_int=1`.

![Touchpoint frequency](figures/touchpoint_frequency_by_channel.png)

## Placement Performance Context

These conversion rates are descriptive. They answer, "when this placement group showed up in a journey, how often did that journey convert?" They do not answer, "how many conversions did this placement cause?"

| Channel | Touchpoints | Journeys Seen | Conversion Rate When Seen |
|---|---:|---:|---:|
"""
    for row in touch_summary.sort_values("conversion_rate_when_seen", ascending=False).itertuples():
        body += f"| {row.channel} | {row.touchpoints:,} | {row.journeys_seen:,} | {fmt_pct(row.conversion_rate_when_seen)} |\n"

    body += f"""
## Attribution Model Comparison

First-touch and last-touch are useful because they are simple. The tradeoff is that each one throws away most of the path. Markov removal uses the sequence: it removes one placement group at a time and checks how much modeled conversion probability falls.

![Attribution comparison](figures/attribution_model_comparison.png)

| Channel | First Touch | Last Touch | Linear | Markov Removal |
|---|---:|---:|---:|---:|
"""
    shares = attribution.pivot(index="channel", columns="method", values="credit_share")
    for channel in shares.index:
        body += (
            f"| {channel} | {fmt_pct(shares.loc[channel, 'First touch'])} | "
            f"{fmt_pct(shares.loc[channel, 'Last touch'])} | "
            f"{fmt_pct(shares.loc[channel, 'Linear'])} | "
            f"{fmt_pct(shares.loc[channel, 'Markov removal'])} |\n"
        )

    body += f"""
## Budget Implication

Under the current pilot-budget assumption, Markov points more money toward `{increase_gap['channel']}` and less toward `{reduction_gap['channel']}`. The largest positive gap is **{increase_gap['channel']} ({fmt_money_k(increase_gap['budget_gap_to_markov'])})**. The largest reduction is **{reduction_gap['channel']} ({fmt_money_k(reduction_gap['budget_gap_to_markov'])})**.

![Budget gap](figures/budget_gap_to_markov.png)

## Scenario Recommendation

| Scenario | Estimated Contribution Lift | Lift % | Incremental ROAS | Tradeoff |
|---|---:|---:|---:|---|
"""
    for row in scenarios.itertuples():
        body += (
            f"| {row.scenario} | {fmt_money_k(row.estimated_revenue_lift)} | "
            f"{fmt_pct(row.estimated_lift_pct)} | {row.incremental_roas:.2f}x | {row.description} |\n"
        )

    body += """
My recommendation is the balanced scenario. It moves enough budget to matter without pretending the model is precise enough to justify a full immediate reallocation.

## Caveats And Assumptions

- The dataset is real Criteo data, but this repo uses one shard and filters to multi-touch users.
- Publisher IDs are anonymized, so the placement labels are readable names I assigned for analysis.
- The dollar layer is assumption-based. Criteo provides sales labels, not advertiser revenue or media budget.
- Markov attribution is correlational. I would validate any real budget move with incrementality testing, geo holdouts, randomized experiments, or media-mix modeling.
"""
    path.write_text(body, encoding="utf-8")


def write_strategy_deck(
    path: Path,
    quality: dict[str, object],
    attribution: pd.DataFrame,
    budget: pd.DataFrame,
    scenarios: pd.DataFrame,
    status_quo: dict[str, float],
) -> None:
    markov = attribution.loc[attribution["method"] == "Markov removal"].sort_values("credit_share", ascending=False)
    last = attribution.loc[attribution["method"] == "Last touch"].set_index("channel")
    top = markov.iloc[0]
    top_gap = budget.sort_values("budget_gap_to_markov", ascending=False).iloc[0]
    reduction = budget.sort_values("budget_gap_to_markov", ascending=True).iloc[0]
    balanced = scenarios.loc[scenarios["scenario"] == "Balanced reallocation"].iloc[0]

    body = f"""# Marketing Attribution & Budget ROI Strategy

CriteoPrivateAd sample analysis
Prepared by Shalom Wu

---

## 1. The Problem

Last-touch attribution is simple, which is why teams use it. The issue is that budget decisions need more than the final touch.

- Last-touch gives all credit to the last observed placement.
- Earlier placements can matter even when they are not last.
- The real question is not "what touched the customer last?" It is "where should the next dollar go?"

---

## 2. What Changed

The biggest bucket is stable, but the smaller placements shift.

- Markov removal gives {top['channel']} the highest credit at {fmt_pct(top['credit_share'])}.
- Last-touch credits the same channel at {fmt_pct(float(last.loc[top['channel'], 'credit_share']))}.
- Sample size: {quality['journeys']:,} multi-touch journeys, {fmt_pct(float(quality['conversion_rate']))} conversion rate.

![Attribution comparison](figures/attribution_model_comparison.png)

---

## 3. Cost Of The Status Quo

If last-touch drove the budget, about {fmt_money_k(status_quo['last_touch_misallocated_budget'])} would land in the wrong place relative to the Markov-informed mix.

- That equals {fmt_pct(status_quo['last_touch_misallocated_budget_share'])} of the assumed pilot budget.
- Biggest increase under Markov: {top_gap['channel']} ({fmt_money_k(top_gap['budget_gap_to_markov'])}).
- Biggest reduction under Markov: {reduction['channel']} ({fmt_money_k(reduction['budget_gap_to_markov'])}).

![Budget gap](figures/budget_gap_to_markov.png)

---

## 4. Reallocation Scenarios

I modeled three levels of change. The more aggressive the shift, the higher the estimated contribution lift, but the less comfortable I would be rolling it out without a test.

| Scenario | Estimated Lift | Incremental ROAS | Tradeoff |
|---|---:|---:|---|
"""
    for row in scenarios.itertuples():
        body += f"| {row.scenario} | {fmt_money_k(row.estimated_revenue_lift)} | {row.incremental_roas:.2f}x | {row.description} |\n"

    body += f"""
![Scenario lift](figures/scenario_revenue_lift.png)

---

## 5. Recommendation

Use the balanced scenario.

- Shift 65% of the gap between current spend and Markov-informed spend.
- Expected assumed contribution lift: {fmt_money_k(balanced['estimated_revenue_lift'])}, or {fmt_pct(balanced['estimated_lift_pct'])}.
- Keep last-touch as a reporting view, not the main budget allocator.
- Validate the recommendation with a holdout or incrementality test before scaling.

---

## 6. How I Would Roll It Out

1. Keep tracking stable for one quarter.
2. Show first-touch, last-touch, linear, and Markov side by side.
3. Move budget in stages, with guardrails on CPA, margin, and conversion volume.
4. Test the biggest proposed shifts before making them permanent.

---

## 7. Method Notes

- Data: processed CriteoPrivateAd sample.
- Grain: one display impression becomes one attribution touchpoint.
- Placement groups: top eight publishers shown separately; the rest grouped as Long-tail placements.
- Models: first-touch, last-touch, linear, and Markov removal.
- Budget layer: assumed pilot spend, assumed contribution per sale, and a simple diminishing-returns curve.

---

## 8. Limits

- Attribution is correlational, not causal.
- The source is real Criteo data, but the publisher names are anonymized.
- The repo uses one shard, not the full CriteoPrivateAd dataset.
- Real deployment would need actual spend, margin, LTV, saturation, and finance-approved contribution economics.
"""
    path.write_text(body, encoding="utf-8")
