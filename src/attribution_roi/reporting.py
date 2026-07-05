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

This project uses a deterministic synthetic marketing attribution dataset generated inside the repository.

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


def write_generation_markdown(path: Path, assumptions: dict[str, object]) -> None:
    body = f"""# Synthetic Data Generation Assumptions

This dataset is synthetic. It is not customer data and should not be represented as real marketing performance.

| Field | Assumption |
|---|---|
| Dataset type | {assumptions['dataset_type']} |
| Journey count | {assumptions['n_journeys']:,} |
| Period | {assumptions['period_start']} to {assumptions['period_end']} |
| Random seed | {assumptions['random_seed']} |
| Grain | {assumptions['grain']} |
| Business context | {assumptions['business_context']} |

## Modeling Logic

- {assumptions['conversion_model']}
- {assumptions['revenue_model']}
- Channels included: {', '.join(assumptions['channels'])}.

The synthetic setup intentionally creates a common attribution problem: lower-funnel channels such as Paid Search, Email, and Direct often appear late in journeys, while awareness and consideration channels help create demand earlier in the path. This lets the project demonstrate why last-touch attribution can misallocate budget.
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

- **Last-touch attribution materially changes channel credit.** The Markov removal model gives the most credit to {top_markov['channel']} at {fmt_pct(top_markov['credit_share'])} of synthetic converted revenue, while last-touch would credit that channel at {fmt_pct(float(last.loc[top_markov['channel'], 'credit_share']))}.
- **The budget issue is not just measurement; it is spend allocation.** A last-touch allocation would misdirect an estimated {fmt_money_k(status_quo['last_touch_misallocated_budget'])}, or {fmt_pct(status_quo['last_touch_misallocated_budget_share'])} of the synthetic quarter's budget, versus the Markov-informed mix.
- **A balanced reallocation is the practical recommendation.** It estimates {fmt_money_k(recommended_scenario['estimated_revenue_lift'])} revenue lift ({fmt_pct(recommended_scenario['estimated_lift_pct'])}) while avoiding the execution risk of a full model-driven swing.
- **This is correlational, not causal.** Attribution models allocate credit across observed journeys; they do not prove incremental lift without experiments or stronger causal design.

## Dataset Profile

The repository uses a deterministic synthetic dataset because a clean, directly usable, well-documented public multi-touch attribution dataset was not selected for this portfolio build. The synthetic dataset contains {quality['rows']:,} touchpoints across {quality['journeys']:,} journeys from {quality['min_touchpoint_date']} to {quality['max_touchpoint_date']}. Journey conversion rate is {fmt_pct(float(quality['conversion_rate']))}; average journey length is {avg_journey_length:.2f} touches.

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

First-touch and last-touch answer simple operational questions, but they throw away most journey context. The Markov removal model asks how much the overall conversion probability falls when a channel is removed from paths, then allocates converted revenue based on that removal effect.

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

| Scenario | Estimated Revenue Lift | Lift % | Incremental ROAS | Tradeoff |
|---|---:|---:|---:|---|
"""
    for row in scenarios.itertuples():
        body += (
            f"| {row.scenario} | {fmt_money_k(row.estimated_revenue_lift)} | "
            f"{fmt_pct(row.estimated_lift_pct)} | {row.incremental_roas:.2f}x | {row.description} |\n"
        )

    body += """
## Caveats And Assumptions

- The dataset is synthetic and calibrated for portfolio demonstration, not a real company's performance history.
- Markov attribution is correlational. It is better than last-touch for using journey sequence information, but it still cannot prove what would have happened without a channel.
- Spend response uses a simple diminishing-returns curve. Real budget decisions should be validated with incrementality tests, geo holdouts, media-mix modeling, or randomized lift studies.
- Revenue is gross synthetic order revenue. A real business case should use contribution margin or customer lifetime value after returns, discounts, and fulfillment cost.
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

Synthetic portfolio analysis for a mid-size e-commerce business  
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
- The synthetic dataset contains {quality['journeys']:,} journeys and a {fmt_pct(float(quality['conversion_rate']))} conversion rate.

![Attribution comparison](figures/attribution_model_comparison.png)

---

## 3. Cost Of The Status Quo

Using last-touch as the budget guide would misallocate an estimated {fmt_money_k(status_quo['last_touch_misallocated_budget'])}.

- That equals {fmt_pct(status_quo['last_touch_misallocated_budget_share'])} of the synthetic quarter budget.
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
- Expected synthetic revenue lift: {fmt_money_k(balanced['estimated_revenue_lift'])}, or {fmt_pct(balanced['estimated_lift_pct'])}.
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

- Dataset: deterministic synthetic customer journeys, clearly labeled as synthetic.
- Grain: one touchpoint row per user journey interaction.
- Baselines: first-touch, last-touch, and linear attribution.
- Data-driven model: Markov chain removal effect, which measures conversion-probability drop when a channel is removed from paths.
- Budget model: current-quarter spend assumption, Markov credit shares, and a diminishing-returns response curve.

---

## 8. Appendix: Limitations

- Attribution is correlational, not causal.
- Synthetic data cannot prove real-world performance.
- Channel costs, gross margin, customer lifetime value, and saturation would need real business inputs.
- Real deployment should reconcile attribution with incrementality tests, media-mix modeling, and finance-approved contribution economics.
"""
    path.write_text(body, encoding="utf-8")
