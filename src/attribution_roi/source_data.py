from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path
from urllib.request import urlretrieve

import pandas as pd

from attribution_roi.config import (
    ASSUMED_CONTRIBUTION_PER_SALE,
    CHANNELS,
    CRITEO_DATASET_CARD_URL,
    CRITEO_SOURCE_URL,
    RAW_CRITEO_PARQUET_PATH,
    RAW_DATA_DIR,
    TOUCHPOINTS_PATH,
)

SOURCE_COLUMNS = [
    "id",
    "user_id",
    "display_order",
    "campaign_id",
    "publisher_id",
    "is_clicked",
    "is_click_landed",
    "nb_sales",
    "sale_delay_after_display_array",
    "click_delay_after_display_array",
]


def download_criteo_source(raw_path: Path = RAW_CRITEO_PARQUET_PATH) -> Path:
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    if not raw_path.exists():
        urlretrieve(CRITEO_SOURCE_URL, raw_path)
    return raw_path


def prepare_criteo_touchpoints(
    raw_path: Path = RAW_CRITEO_PARQUET_PATH,
    output_path: Path = TOUCHPOINTS_PATH,
    *,
    source_day_int: int = 1,
    min_touches_per_user: int = 2,
    top_publishers: int = 8,
    contribution_per_sale: float = ASSUMED_CONTRIBUTION_PER_SALE,
) -> pd.DataFrame:
    """Create a touchpoint-level attribution sample from CriteoPrivateAd."""
    if not raw_path.exists():
        raise FileNotFoundError(
            f"Raw Criteo shard not found at {raw_path}. Run scripts/download_source_data.py first."
        )

    raw = pd.read_parquet(raw_path, columns=SOURCE_COLUMNS)
    raw = raw.copy()
    raw["sales_count_row"] = raw["nb_sales"].fillna(0).astype(float)
    raw["is_click_landed"] = raw["is_click_landed"].fillna(0).astype(int)
    raw["is_clicked"] = raw["is_clicked"].fillna(0).astype(int)

    user_summary = (
        raw.groupby("user_id")
        .agg(touchpoints=("id", "size"), sales_count=("sales_count_row", "sum"))
        .reset_index()
    )
    keep_users = user_summary.loc[
        user_summary["touchpoints"] >= min_touches_per_user, "user_id"
    ]
    sample = raw.loc[raw["user_id"].isin(keep_users)].copy()

    publisher_rank = (
        sample.groupby("publisher_id")
        .agg(touchpoints=("id", "size"), sales_count=("sales_count_row", "sum"))
        .sort_values(["touchpoints", "sales_count"], ascending=False)
        .head(top_publishers)
        .reset_index()
    )
    publisher_map = {
        row.publisher_id: f"Publisher {index:02d}"
        for index, row in enumerate(publisher_rank.itertuples(), start=1)
    }
    sample["channel"] = sample["publisher_id"].map(publisher_map).fillna("Long-tail placements")

    relative_date = date(2025, 1, 1) + timedelta(days=source_day_int - 1)
    sample = sample.sort_values(["user_id", "display_order", "id"]).reset_index(drop=True)
    sample["touchpoint_sequence"] = sample.groupby("user_id").cumcount() + 1

    journey_sales = sample.groupby("user_id")["sales_count_row"].sum().rename("sales_count")
    sample = sample.merge(journey_sales, on="user_id", how="left")
    sample["converted"] = (sample["sales_count"] > 0).astype(int)
    sample["revenue"] = sample["sales_count"] * contribution_per_sale
    sample["conversion_date"] = sample["converted"].map(
        {1: relative_date.isoformat(), 0: ""}
    )

    output = pd.DataFrame(
        {
            "user_id": sample["user_id"],
            "journey_id": "D01_" + sample["user_id"].astype(str),
            "touchpoint_id": sample["id"],
            "touchpoint_sequence": sample["touchpoint_sequence"],
            "touchpoint_date": relative_date.isoformat(),
            "source_day_int": source_day_int,
            "channel": sample["channel"],
            "channel_stage": "Display placement",
            "converted": sample["converted"],
            "conversion_date": sample["conversion_date"],
            "sales_count": sample["sales_count"],
            "revenue": sample["revenue"],
            "is_clicked": sample["is_clicked"],
            "is_click_landed": sample["is_click_landed"],
            "source_campaign_id": sample["campaign_id"],
            "source_publisher_id": sample["publisher_id"],
        }
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(output_path, index=False)
    return output


def source_assumptions() -> dict[str, object]:
    return {
        "dataset_type": "real public dataset sample",
        "source_name": "CriteoPrivateAd",
        "source_url": CRITEO_DATASET_CARD_URL,
        "source_file_url": CRITEO_SOURCE_URL,
        "raw_local_path": "data/raw/criteo_day1_part-00238.parquet",
        "processed_local_path": "data/processed/criteo_touchpoints_sample.csv",
        "grain": "one display-ad impression row transformed into one attribution touchpoint",
        "source_period": "Criteo 30-day live traffic sample; repo sample uses day_int=1 shard part-00238",
        "sample_filter": "users with at least two impressions in the downloaded shard",
        "channel_definition": (
            "channel is an anonymized publisher placement group. Top eight publishers by touch volume "
            "are mapped to Publisher 01-08; the rest are grouped as Long-tail placements."
        ),
        "date_handling": (
            "CriteoPrivateAd partitions by relative day_int, not real calendar dates. The repo maps "
            "day_int=1 to 2025-01-01 as a relative plotting date."
        ),
        "value_assumption": (
            f"Revenue is modeled as sales_count * ${ASSUMED_CONTRIBUTION_PER_SALE:,.0f} assumed contribution per sale "
            "because source data provides sales counts but not advertiser revenue."
        ),
        "channels": CHANNELS,
    }
