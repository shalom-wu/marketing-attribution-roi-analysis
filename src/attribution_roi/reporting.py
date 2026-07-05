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
    body = f"""# Data Quality Report

This project uses a processed sample from the public CriteoPrivateAd dataset.

| Check | Result |
|---|---:|
| Touchpoint rows | {quality['rows']:,} |
| Customer journeys | {quality['journeys']:,} |
| Converted journeys | {quality['converted_journeys']:,} |
| Journey conversion rate | {fmt_pct(float(quality['conversion_rate']))} |
| Duplicate touchpoint IDs | {quality['duplicate_touchpoint_ids']:,} |
| Invalid channels | {', '.join(quality['invalid_channels']) if quality['invalid_channels'] else 'None'} |
| Date range | {quality['min_touchpoint_date']} to {quality['max_touchpoint_date']} |

Null counts shown below are expected for `conversion_date`, because non-converting journeys do not have a conversion date.

```json
{json.dumps(quality['null_counts'], indent=2)}
```
"""
    path.write_text(body, encoding="utf-8")


def write_source_markdown(path: Path, assumptions: dict[str, object]) -> None:
    body = f"""# Source Data Assumptions

This dataset sample is sourced from CriteoPrivateAd, a public anonymized Criteo advertising dataset hosted on Hugging Face. The repo keeps a processed sample rather than the raw Parquet shard.

| Field | Assumption |
|---|---|
| Dataset type | {assumptions['dataset_type']} |
| Source | [{assumptions['source_name']}]({assumptions['source_url']}) |
| Source file | {assumptions['source_file_url']} |
| Grain | {assumptions['grain']} |
| Source period | {assumptions['source_period']} |
| Sample filter | {assumptions['sample_filter']} |

## Transformation Notes

- {assumptions['channel_definition']}
- {assumptions['date_handling']}
- {assumptions['value_assumption']}
- Channels included: {', '.join(assumptions['channels'])}.

The source contains real anonymized display-ad impressions, campaign/publisher IDs, clicks, and sales labels. It does not contain named marketing channels, actual calendar dates, advertiser revenue, or a finance-approved media budget.
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

## Executive Summary

- **Last-touch attribution materially changes channel credit.** The Markov removal model gives the most credit to {top_markov['channel']} at {fmt_pct(top_markov['credit_share'])} of assumed contribution value, while last-touch would credit that channel at {fmt_pct(float(last.loc[top_markov['channel'], 'credit_share']))}.
- **The budget issue is not just measurement; it is spend allocation.** A last-touch allocation would misdirect an estimated {fmt_money_k(status_quo['last_touch_misallocated_budget'])}, or {fmt_pct(status_quo['last_touch_misallocated_budget_share'])} of the assumed pilot budget, versus the Markov-informed mix.
- **A balanced reallocation is the practical recommendation.** It estimates {fmt_money_k(recommended_scenario['estimated_revenue_lift'])} assumed contribution lift ({fmt_pct(recommended_scenario['estimated_lift_pct'])}) while avoiding the execution risk of a full model-driven swing.
- **This is correlational, not causal.** Attribution models allocate credit across observed journeys; they do not prove incremental lift without experiments or stronger causal design.

## Dataset Profile

The repository uses a processed sample from CriteoPrivateAd, a public anonymized Criteo advertising dataset hosted on Hugging Face. The sample contains {quality['rows']:,} display touchpoints across {quality['journeys']:,} multi-touch user journeys. Journey conversion rate is {fmt_pct(float(quality['conversion_rate']))}; average journey length is {avg_journey_length:.2f} touches. Criteo provides relative day partitions rather than calendar dates, so the repo maps `day_int=1` to a relative plotting date.

![Touchpoint frequency](figures/touchpoint_frequency_by_channel.png)

## Channel Performance Context

Channel exposure conversion rates are descriptive. They should be read as "journeys that included this channel converted at this rate," not as a causal lift claim.

| Channel | Touchpoints | Journeys Seen | Conversion Rate When Seen |
|---|---:|---:|---:|
"""
    for row in touch_summary.sort_values("conversion_rate_when_seen", ascending=False).itertuples():
        body += f"| {row.channel} | {row.touchpoints:,} | {row.journeys_seen:,} | {fmt_pct(row.conversion_rate_when_seen)} |\n"

    body += f"""
## Attribution Model Comparison

First-touch and last-touch answer simple operational questions, but they throw away most journey context. The Markov removal model asks how much the overall conversion probability falls when a publisher placement group is removed from paths, then allocates assumed contribution value based on that removal effect.

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

The largest positive Markov budget gap is {increase_gap['channel']} at {fmt_money_k(increase_gap['budget_gap_to_markov'])}; the largest reduction is {reduction_gap['channel']} at {fmt_money_k(reduction_gap['budget_gap_to_markov'])}. Positive gaps indicate channels that would receive more budget under the Markov-informed allocation; negative gaps indicate reductions.

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
## Caveats And Assumptions

- The dataset sample is real anonymized Criteo advertising data, but the repo filters to one day-one Parquet shard and multi-touch users.
- Markov attribution is correlational. It is better than last-touch for using journey sequence information, but it still cannot prove what would have happened without a channel.
- Dollarized spend and revenue are assumptions because this Criteo sample provides sales labels but not advertiser revenue or a channel budget.
- Spend response uses a simple diminishing-returns curve. Real budget decisions should be validated with incrementality tests, geo holdouts, media-mix modeling, or randomized lift studies.
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

    body = f"""# Marketing Channel Attribution & Budget ROI Strategy

Sourced CriteoPrivateAd sample analysis for a mid-size e-commerce business  
Prepared by Shalom Wu

---

## 1. Problem Framing

Last-touch attribution is easy to explain but risky for budget decisions.

- It gives 100% credit to the final observed channel before conversion.
- That can over-credit demand-capture channels and under-credit channels that created the demand earlier.
- The business problem is not "which channel touched the customer last?" It is "where should the next budget dollar go?"

---

## 2. Key Finding

Attribution method choice materially changes channel credit.

- Markov removal gives {top['channel']} the highest credit at {fmt_pct(top['credit_share'])}.
- Last-touch credits the same channel at {fmt_pct(float(last.loc[top['channel'], 'credit_share']))}.
- The sourced Criteo sample contains {quality['journeys']:,} multi-touch journeys and a {fmt_pct(float(quality['conversion_rate']))} conversion rate.

![Attribution comparison](figures/attribution_model_comparison.png)

---

## 3. Cost Of The Status Quo

Using last-touch as the budget guide would misallocate an estimated {fmt_money_k(status_quo['last_touch_misallocated_budget'])}.

- That equals {fmt_pct(status_quo['last_touch_misallocated_budget_share'])} of the assumed pilot budget.
- The biggest increase under Markov is {top_gap['channel']} ({fmt_money_k(top_gap['budget_gap_to_markov'])}).
- The biggest reduction is {reduction['channel']} ({fmt_money_k(reduction['budget_gap_to_markov'])}).

![Budget gap](figures/budget_gap_to_markov.png)

---

## 4. Reallocation Scenarios

Three scenarios translate attribution into operating choices.

| Scenario | Estimated Lift | Incremental ROAS | Tradeoff |
|---|---:|---:|---|
"""
    for row in scenarios.itertuples():
        body += f"| {row.scenario} | {fmt_money_k(row.estimated_revenue_lift)} | {row.incremental_roas:.2f}x | {row.description} |\n"

    body += f"""
![Scenario lift](figures/scenario_revenue_lift.png)

---

## 5. Recommended Approach

Use a balanced reallocation, not a full swing to the model.

- Shift 65% of the gap between current spend and Markov-informed spend.
- Expected assumed contribution lift: {fmt_money_k(balanced['estimated_revenue_lift'])}, or {fmt_pct(balanced['estimated_lift_pct'])}.
- Keep last-touch reporting for operational diagnostics, but do not use it as the primary budget allocator.
- Validate the recommendation with a holdout or incrementality test before scaling.

---

## 6. Deployment Strategy

1. Keep current tracking taxonomy stable for one quarter.
2. Report first-touch, last-touch, linear, and Markov credit side by side.
3. Move budget in staged increments with guardrails on CPA, margin, and conversion volume.
4. Use experiments to calibrate causal lift where the attribution model suggests material spend shifts.

---

## 7. Appendix: Methodology

- Dataset: processed sample from CriteoPrivateAd public anonymized advertising data.
- Grain: one display impression transformed into one attribution touchpoint.
- Channel definition: anonymized publisher placement groups, with the top eight publishers shown separately and the remaining publishers grouped as Long-tail placements.
- Baselines: first-touch, last-touch, and linear attribution.
- Data-driven model: Markov chain removal effect, which measures conversion-probability drop when a channel is removed from paths.
- Budget model: assumed pilot spend, assumed contribution per sale, Markov credit shares, and a diminishing-returns response curve.

---

## 8. Appendix: Limitations

- Attribution is correlational, not causal.
- The sample is real Criteo data, but the channel names are anonymized and the repo uses one downloaded shard, not the full 100M-row dataset.
- Channel costs, gross margin, customer lifetime value, and saturation would need real business inputs.
- Real deployment should reconcile attribution with incrementality tests, media-mix modeling, and finance-approved contribution economics.
"""
    path.write_text(body, encoding="utf-8")
