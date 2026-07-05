from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import exp

import numpy as np
import pandas as pd

from attribution_roi.config import CHANNELS, CHANNEL_STAGE, RANDOM_SEED


@dataclass(frozen=True)
class SyntheticConfig:
    n_journeys: int = 15000
    start_date: str = "2026-01-01"
    end_date: str = "2026-03-31"
    seed: int = RANDOM_SEED


FIRST_TOUCH_PROBS = {
    "Display": 0.20,
    "Paid Social": 0.19,
    "Referral": 0.10,
    "Organic Search": 0.18,
    "Paid Search": 0.15,
    "Affiliate": 0.06,
    "Email": 0.07,
    "Direct": 0.05,
}

MIDDLE_TOUCH_PROBS = {
    "Display": 0.10,
    "Paid Social": 0.14,
    "Referral": 0.07,
    "Organic Search": 0.18,
    "Paid Search": 0.18,
    "Affiliate": 0.08,
    "Email": 0.14,
    "Direct": 0.11,
}

LAST_TOUCH_PROBS = {
    "Display": 0.04,
    "Paid Social": 0.06,
    "Referral": 0.05,
    "Organic Search": 0.14,
    "Paid Search": 0.25,
    "Affiliate": 0.08,
    "Email": 0.16,
    "Direct": 0.22,
}

CHANNEL_CONVERSION_EFFECT = {
    "Display": 0.08,
    "Paid Social": 0.18,
    "Referral": 0.30,
    "Organic Search": 0.34,
    "Paid Search": 0.42,
    "Affiliate": 0.24,
    "Email": 0.52,
    "Direct": 0.15,
}


def _choice(rng: np.random.Generator, probs: dict[str, float]) -> str:
    labels = list(probs)
    weights = np.array([probs[label] for label in labels], dtype=float)
    weights = weights / weights.sum()
    return str(rng.choice(labels, p=weights))


def _sigmoid(value: float) -> float:
    return 1.0 / (1.0 + exp(-value))


def _generate_path(rng: np.random.Generator, length: int) -> list[str]:
    path: list[str] = []
    for index in range(length):
        if index == 0:
            channel = _choice(rng, FIRST_TOUCH_PROBS)
        elif index == length - 1:
            channel = _choice(rng, LAST_TOUCH_PROBS)
        else:
            channel = _choice(rng, MIDDLE_TOUCH_PROBS)

        # Keep paths realistic by reducing immediate duplicate touches.
        if path and channel == path[-1] and rng.random() < 0.55:
            channel = _choice(rng, MIDDLE_TOUCH_PROBS if index < length - 1 else LAST_TOUCH_PROBS)
        path.append(channel)
    return path


def _conversion_probability(path: list[str]) -> float:
    unique_channels = set(path)
    score = -3.25
    score += sum(CHANNEL_CONVERSION_EFFECT[channel] for channel in unique_channels)

    upper_funnel_seen = bool(unique_channels & {"Display", "Paid Social"})
    demand_capture_seen = bool(unique_channels & {"Paid Search", "Email", "Direct"})
    if upper_funnel_seen and demand_capture_seen:
        score += 0.34
    if "Referral" in unique_channels and "Organic Search" in unique_channels:
        score += 0.18
    if path[-1] in {"Paid Search", "Email"}:
        score += 0.22
    if path[-1] == "Direct":
        score += 0.08

    journey_length = len(path)
    score += min(journey_length - 1, 4) * 0.08
    if journey_length >= 7:
        score -= 0.20

    duplicate_touches = journey_length - len(unique_channels)
    score -= duplicate_touches * 0.05
    return _sigmoid(score)


def generate_synthetic_touchpoints(config: SyntheticConfig | None = None) -> pd.DataFrame:
    """Generate one row per marketing touchpoint for a synthetic customer journey."""
    cfg = config or SyntheticConfig()
    rng = np.random.default_rng(cfg.seed)
    start = datetime.fromisoformat(cfg.start_date)
    end = datetime.fromisoformat(cfg.end_date)
    available_days = max((end - start).days, 1)

    rows: list[dict[str, object]] = []
    for journey_number in range(1, cfg.n_journeys + 1):
        journey_length = int(np.clip(1 + rng.poisson(2.15), 1, 8))
        path = _generate_path(rng, journey_length)
        conversion_probability = _conversion_probability(path)
        converted = bool(rng.random() < conversion_probability)

        start_offset = int(rng.integers(0, max(available_days - 21, 1)))
        gaps = rng.integers(0, 6, size=journey_length).cumsum()
        touch_dates = [start + timedelta(days=int(start_offset + gap)) for gap in gaps]
        conversion_date = touch_dates[-1] + timedelta(days=int(rng.integers(0, 3))) if converted else None

        revenue = 0.0
        if converted:
            # Lognormal average order value with a sensible cap for presentation.
            revenue = float(np.clip(rng.lognormal(mean=5.12, sigma=0.42), 45, 650))

        user_id = f"U{journey_number:06d}"
        journey_id = f"J{journey_number:06d}"
        for touch_index, (channel, touch_date) in enumerate(zip(path, touch_dates), start=1):
            rows.append(
                {
                    "user_id": user_id,
                    "journey_id": journey_id,
                    "touchpoint_id": f"{journey_id}_T{touch_index:02d}",
                    "touchpoint_sequence": touch_index,
                    "touchpoint_date": touch_date.date().isoformat(),
                    "channel": channel,
                    "channel_stage": CHANNEL_STAGE[channel],
                    "converted": int(converted),
                    "conversion_probability": round(conversion_probability, 5),
                    "conversion_date": conversion_date.date().isoformat() if converted else "",
                    "revenue": round(revenue, 2),
                }
            )

    return pd.DataFrame(rows)


def generation_assumptions(config: SyntheticConfig | None = None) -> dict[str, object]:
    cfg = config or SyntheticConfig()
    return {
        "dataset_type": "synthetic",
        "n_journeys": cfg.n_journeys,
        "period_start": cfg.start_date,
        "period_end": cfg.end_date,
        "random_seed": cfg.seed,
        "grain": "one row per customer journey touchpoint",
        "channels": CHANNELS,
        "conversion_model": (
            "Synthetic conversion probability is a logistic-style function of channel presence, "
            "journey length, lower-funnel final touches, and upper-plus-lower-funnel synergy."
        ),
        "revenue_model": "Converted journeys receive capped lognormal synthetic order revenue.",
        "business_context": "mid-size e-commerce business; no fabricated brand name or real customer data",
    }
