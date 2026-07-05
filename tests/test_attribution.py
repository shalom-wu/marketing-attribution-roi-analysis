import pandas as pd
import pytest

from attribution_roi.attribution import (
    attribution_summary,
    first_touch_attribution,
    last_touch_attribution,
    linear_attribution,
    markov_removal_attribution,
)


@pytest.fixture
def sample_journeys():
    return pd.DataFrame(
        [
            {"journey_id": "J1", "converted": 1, "revenue": 100.0, "path": ["Display", "Paid Search"]},
            {"journey_id": "J2", "converted": 1, "revenue": 60.0, "path": ["Email"]},
            {"journey_id": "J3", "converted": 0, "revenue": 0.0, "path": ["Display", "Direct"]},
        ]
    )


def test_first_and_last_touch(sample_journeys):
    first = first_touch_attribution(sample_journeys)
    last = last_touch_attribution(sample_journeys)

    assert first["Display"] == 100.0
    assert first["Email"] == 60.0
    assert last["Paid Search"] == 100.0
    assert last["Email"] == 60.0


def test_linear_splits_multi_touch_credit(sample_journeys):
    linear = linear_attribution(sample_journeys)

    assert linear["Display"] == 50.0
    assert linear["Paid Search"] == 50.0
    assert linear["Email"] == 60.0


def test_markov_credit_sums_to_converted_revenue(sample_journeys):
    markov = markov_removal_attribution(sample_journeys)

    assert sum(markov.values()) == pytest.approx(160.0)
    assert all(value >= 0 for value in markov.values())


def test_attribution_summary_has_all_methods(sample_journeys):
    summary = attribution_summary(sample_journeys)

    assert set(summary["method"]) == {"First touch", "Last touch", "Linear", "Markov removal"}
    assert summary.groupby("method")["credit_value"].sum().to_dict()["Markov removal"] == pytest.approx(160.0)
