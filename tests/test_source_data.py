from uuid import uuid4
from pathlib import Path

import pandas as pd

from attribution_roi.source_data import prepare_criteo_touchpoints


def test_prepare_criteo_touchpoints_from_small_parquet():
    scratch = Path("tests/_tmp_source_data") / uuid4().hex
    scratch.mkdir(parents=True)
    raw_path = scratch / "raw.parquet"
    output_path = scratch / "touchpoints.csv"
    raw = pd.DataFrame(
        [
            {
                "id": "a",
                "user_id": "u1",
                "display_order": 1,
                "campaign_id": 10,
                "publisher_id": 100.0,
                "is_clicked": 1,
                "is_click_landed": 1.0,
                "nb_sales": None,
                "sale_delay_after_display_array": [],
                "click_delay_after_display_array": [],
            },
            {
                "id": "b",
                "user_id": "u1",
                "display_order": 2,
                "campaign_id": 11,
                "publisher_id": 200.0,
                "is_clicked": 1,
                "is_click_landed": 1.0,
                "nb_sales": 1.0,
                "sale_delay_after_display_array": [0],
                "click_delay_after_display_array": [0],
            },
            {
                "id": "c",
                "user_id": "u2",
                "display_order": 1,
                "campaign_id": 10,
                "publisher_id": 100.0,
                "is_clicked": 0,
                "is_click_landed": 0.0,
                "nb_sales": None,
                "sale_delay_after_display_array": [],
                "click_delay_after_display_array": [],
            },
        ]
    )
    raw.to_parquet(raw_path)

    result = prepare_criteo_touchpoints(
        Path(raw_path),
        Path(output_path),
        min_touches_per_user=2,
        top_publishers=1,
        contribution_per_sale=120,
    )

    assert output_path.exists()
    assert result["journey_id"].nunique() == 1
    assert result["converted"].max() == 1
    assert result["revenue"].max() == 120
