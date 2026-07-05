import pandas as pd

from attribution_roi.budget import budget_recommendation, scenario_summary, status_quo_cost
from attribution_roi.config import CHANNELS


def _summary():
    rows = []
    for method in ["Last touch", "Markov removal"]:
        for index, channel in enumerate(CHANNELS):
            share = (index + 1) / sum(range(1, len(CHANNELS) + 1))
            if method == "Last touch":
                share = 1 / len(CHANNELS)
            rows.append(
                {
                    "method": method,
                    "channel": channel,
                    "credit_value": share * 100000,
                    "credit_share": share,
                }
            )
    return pd.DataFrame(rows)


def test_budget_recommendation_preserves_total_budget():
    budget = budget_recommendation(_summary())

    assert round(budget["current_budget"].sum(), 2) == round(budget["markov_recommended_budget"].sum(), 2)
    assert set(budget["channel"]) == set(CHANNELS)


def test_scenarios_return_positive_budget_case():
    budget = budget_recommendation(_summary())
    scenarios = scenario_summary(budget)
    status = status_quo_cost(budget)

    assert len(scenarios) == 3
    assert scenarios["total_budget"].nunique() == 1
    assert status["last_touch_misallocated_budget"] >= 0
