from __future__ import annotations

import pandas as pd

from attribution_roi.config import CHANNELS, CURRENT_QUARTER_BUDGET


def budget_recommendation(attribution_summary: pd.DataFrame) -> pd.DataFrame:
    markov = (
        attribution_summary.loc[attribution_summary["method"] == "Markov removal"]
        .set_index("channel")
        .reindex(CHANNELS)
    )
    last_touch = (
        attribution_summary.loc[attribution_summary["method"] == "Last touch"]
        .set_index("channel")
        .reindex(CHANNELS)
    )
    total_budget = float(sum(CURRENT_QUARTER_BUDGET.values()))

    rows = []
    for channel in CHANNELS:
        current_budget = float(CURRENT_QUARTER_BUDGET[channel])
        markov_credit_share = float(markov.loc[channel, "credit_share"])
        last_touch_share = float(last_touch.loc[channel, "credit_share"])
        markov_budget = total_budget * markov_credit_share
        last_touch_budget = total_budget * last_touch_share
        credit_value = float(markov.loc[channel, "credit_value"])
        rows.append(
            {
                "channel": channel,
                "current_budget": current_budget,
                "current_budget_share": current_budget / total_budget,
                "last_touch_budget_if_used": last_touch_budget,
                "markov_recommended_budget": markov_budget,
                "budget_gap_to_markov": markov_budget - current_budget,
                "last_touch_vs_markov_gap": last_touch_budget - markov_budget,
                "markov_credit_value": credit_value,
                "markov_credit_share": markov_credit_share,
                "attributed_roas": credit_value / current_budget if current_budget else 0.0,
            }
        )
    return pd.DataFrame(rows)


def status_quo_cost(budget: pd.DataFrame) -> dict[str, float]:
    overallocated = budget["last_touch_vs_markov_gap"].clip(lower=0).sum()
    total_budget = budget["current_budget"].sum()
    return {
        "last_touch_misallocated_budget": float(overallocated),
        "last_touch_misallocated_budget_share": float(overallocated / total_budget if total_budget else 0.0),
    }


def scenario_summary(budget: pd.DataFrame, elasticity: float = 0.65) -> pd.DataFrame:
    """Estimate scenario revenue with a simple diminishing-returns response curve."""
    total_budget = float(budget["current_budget"].sum())
    base_revenue = float(budget["markov_credit_value"].sum())
    scenario_specs = [
        ("Conservative rebalance", 0.35, "Move partway toward Markov credit; lowest disruption."),
        ("Balanced reallocation", 0.65, "Meaningful shift while keeping channel mix diversified."),
        ("Aggressive Markov target", 1.00, "Fully align budget with Markov credit; highest execution risk."),
    ]

    rows = []
    for scenario, shift_fraction, description in scenario_specs:
        scenario_budget = budget["current_budget"] + shift_fraction * budget["budget_gap_to_markov"]
        scenario_budget = scenario_budget.clip(lower=0)
        scenario_budget = scenario_budget * (total_budget / scenario_budget.sum())
        response_ratio = (scenario_budget / budget["current_budget"]).replace([float("inf"), -float("inf")], 0)
        estimated_revenue = float((budget["markov_credit_value"] * (response_ratio ** elasticity)).sum())
        estimated_revenue_lift = estimated_revenue - base_revenue
        budget_shifted = float((scenario_budget - budget["current_budget"]).abs().sum() / 2)
        rows.append(
            {
                "scenario": scenario,
                "description": description,
                "shift_fraction_to_markov": shift_fraction,
                "total_budget": total_budget,
                "budget_shifted": budget_shifted,
                "estimated_revenue": estimated_revenue,
                "estimated_revenue_lift": estimated_revenue_lift,
                "estimated_lift_pct": (estimated_revenue / base_revenue - 1.0) if base_revenue else 0.0,
                "incremental_roas": estimated_revenue_lift / budget_shifted if budget_shifted else 0.0,
            }
        )
    return pd.DataFrame(rows)
