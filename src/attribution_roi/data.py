from __future__ import annotations

from collections import Counter

import pandas as pd

from attribution_roi.config import CHANNELS

REQUIRED_COLUMNS = {
    "user_id",
    "journey_id",
    "touchpoint_id",
    "touchpoint_sequence",
    "touchpoint_date",
    "channel",
    "converted",
    "revenue",
}


def load_touchpoints(path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["touchpoint_date"])
    if "conversion_date" in df.columns:
        df["conversion_date"] = pd.to_datetime(df["conversion_date"], errors="coerce")
    return clean_touchpoints(df)


def clean_touchpoints(df: pd.DataFrame) -> pd.DataFrame:
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    cleaned = df.copy()
    cleaned["channel"] = cleaned["channel"].astype(str).str.strip()
    cleaned["converted"] = cleaned["converted"].astype(int)
    cleaned["revenue"] = cleaned["revenue"].astype(float)
    cleaned["touchpoint_sequence"] = cleaned["touchpoint_sequence"].astype(int)
    cleaned = cleaned.sort_values(["journey_id", "touchpoint_sequence", "touchpoint_date"])
    return cleaned


def data_quality_report(df: pd.DataFrame) -> dict[str, object]:
    duplicate_touchpoints = int(df["touchpoint_id"].duplicated().sum())
    invalid_channels = sorted(set(df["channel"]) - set(CHANNELS))
    null_counts = df.isna().sum().to_dict()
    journeys = journey_table(df)
    return {
        "rows": int(len(df)),
        "journeys": int(journeys["journey_id"].nunique()),
        "converted_journeys": int(journeys["converted"].sum()),
        "conversion_rate": float(journeys["converted"].mean()),
        "duplicate_touchpoint_ids": duplicate_touchpoints,
        "invalid_channels": invalid_channels,
        "null_counts": {key: int(value) for key, value in null_counts.items() if int(value) > 0},
        "min_touchpoint_date": df["touchpoint_date"].min().date().isoformat(),
        "max_touchpoint_date": df["touchpoint_date"].max().date().isoformat(),
    }


def journey_table(df: pd.DataFrame) -> pd.DataFrame:
    ordered = df.sort_values(["journey_id", "touchpoint_sequence"])
    grouped = ordered.groupby("journey_id", sort=False)
    journeys = grouped.agg(
        user_id=("user_id", "first"),
        converted=("converted", "max"),
        revenue=("revenue", "max"),
        first_touch_date=("touchpoint_date", "min"),
        last_touch_date=("touchpoint_date", "max"),
        journey_length=("touchpoint_id", "count"),
    ).reset_index()
    paths = grouped["channel"].apply(list).reset_index(name="path")
    journeys = journeys.merge(paths, on="journey_id", how="left")
    journeys["path_string"] = journeys["path"].apply(lambda path: " > ".join(path))
    journeys["days_in_journey"] = (
        journeys["last_touch_date"] - journeys["first_touch_date"]
    ).dt.days.clip(lower=0)
    return journeys


def channel_touch_summary(df: pd.DataFrame) -> pd.DataFrame:
    journeys = journey_table(df)
    rows: list[dict[str, object]] = []
    for channel in CHANNELS:
        channel_rows = df.loc[df["channel"] == channel]
        journey_ids = set(channel_rows["journey_id"])
        exposed = journeys.loc[journeys["journey_id"].isin(journey_ids)]
        converted_journeys = int(exposed["converted"].sum())
        rows.append(
            {
                "channel": channel,
                "touchpoints": int(len(channel_rows)),
                "journeys_seen": int(len(exposed)),
                "converted_journeys_seen": converted_journeys,
                "conversion_rate_when_seen": converted_journeys / len(exposed) if len(exposed) else 0.0,
                "touchpoint_share": len(channel_rows) / len(df) if len(df) else 0.0,
            }
        )
    return pd.DataFrame(rows)


def journey_pattern_summary(journeys: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    pattern_counts = Counter(journeys["path_string"])
    rows = []
    for pattern, count in pattern_counts.most_common(top_n):
        part = journeys.loc[journeys["path_string"] == pattern]
        rows.append(
            {
                "path_string": pattern,
                "journeys": int(count),
                "conversion_rate": float(part["converted"].mean()),
                "avg_revenue_per_journey": float(part["revenue"].mean()),
            }
        )
    return pd.DataFrame(rows)
