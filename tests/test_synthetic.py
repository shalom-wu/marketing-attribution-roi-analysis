from attribution_roi.synthetic import SyntheticConfig, generate_synthetic_touchpoints


def test_synthetic_generation_schema_and_determinism():
    config = SyntheticConfig(n_journeys=25, seed=123)
    first = generate_synthetic_touchpoints(config)
    second = generate_synthetic_touchpoints(config)

    assert first.equals(second)
    assert first["journey_id"].nunique() == 25
    assert {"user_id", "journey_id", "touchpoint_date", "channel", "converted", "revenue"}.issubset(first.columns)
    assert first["touchpoint_sequence"].min() == 1
