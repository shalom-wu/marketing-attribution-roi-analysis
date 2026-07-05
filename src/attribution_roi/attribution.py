from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from attribution_roi.config import CHANNELS

START = "__START__"
CONVERSION = "__CONVERSION__"
NULL = "__NULL__"


def _empty_credit() -> dict[str, float]:
    return {channel: 0.0 for channel in CHANNELS}


def first_touch_attribution(journeys: pd.DataFrame) -> dict[str, float]:
    credit = _empty_credit()
    for row in journeys.loc[journeys["converted"] == 1].itertuples():
        credit[row.path[0]] += float(row.revenue)
    return credit


def last_touch_attribution(journeys: pd.DataFrame) -> dict[str, float]:
    credit = _empty_credit()
    for row in journeys.loc[journeys["converted"] == 1].itertuples():
        credit[row.path[-1]] += float(row.revenue)
    return credit


def linear_attribution(journeys: pd.DataFrame) -> dict[str, float]:
    credit = _empty_credit()
    for row in journeys.loc[journeys["converted"] == 1].itertuples():
        path = list(row.path)
        per_touch_credit = float(row.revenue) / len(path)
        for channel in path:
            credit[channel] += per_touch_credit
    return credit


def transition_probabilities(journeys: pd.DataFrame) -> dict[str, dict[str, float]]:
    counts: dict[str, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in journeys.itertuples():
        outcome = CONVERSION if int(row.converted) == 1 else NULL
        sequence = [START, *list(row.path), outcome]
        for origin, destination in zip(sequence, sequence[1:]):
            counts[origin][destination] += 1.0

    transitions: dict[str, dict[str, float]] = {}
    for origin, destinations in counts.items():
        total = sum(destinations.values())
        transitions[origin] = {
            destination: value / total for destination, value in destinations.items()
        }
    return transitions


def conversion_absorption_probability(transitions: dict[str, dict[str, float]]) -> float:
    states = sorted(
        state
        for state in transitions
        if state not in {CONVERSION, NULL}
    )
    if START not in states:
        return 0.0

    index = {state: position for position, state in enumerate(states)}
    q = np.zeros((len(states), len(states)))
    r_conversion = np.zeros(len(states))

    for origin, destinations in transitions.items():
        if origin not in index:
            continue
        origin_index = index[origin]
        for destination, probability in destinations.items():
            if destination == CONVERSION:
                r_conversion[origin_index] += probability
            elif destination == NULL:
                continue
            elif destination in index:
                q[origin_index, index[destination]] += probability

    identity = np.eye(len(states))
    try:
        absorption = np.linalg.solve(identity - q, r_conversion)
    except np.linalg.LinAlgError:
        absorption = np.linalg.pinv(identity - q).dot(r_conversion)
    return float(np.clip(absorption[index[START]], 0.0, 1.0))


def remove_channel_from_transitions(
    transitions: dict[str, dict[str, float]], channel: str
) -> dict[str, dict[str, float]]:
    """Remove a channel and redirect traffic that would enter it to non-conversion.

    This removal-effect interpretation asks what happens if a channel is no
    longer available in the observed journey graph. Probability mass that would
    have moved into the removed channel is sent to the null outcome rather than
    redistributed to other channels, which avoids pretending the same customers
    would automatically find the next-best path.
    """
    removed: dict[str, dict[str, float]] = {}
    for origin, destinations in transitions.items():
        if origin == channel:
            continue
        filtered: dict[str, float] = {}
        null_probability = 0.0
        for destination, probability in destinations.items():
            if destination == channel:
                null_probability += probability
            else:
                filtered[destination] = filtered.get(destination, 0.0) + probability
        if null_probability:
            filtered[NULL] = filtered.get(NULL, 0.0) + null_probability
        removed[origin] = filtered or {NULL: 1.0}
    return removed


def markov_removal_attribution(journeys: pd.DataFrame) -> dict[str, float]:
    transitions = transition_probabilities(journeys)
    baseline_probability = conversion_absorption_probability(transitions)
    total_revenue = float(journeys.loc[journeys["converted"] == 1, "revenue"].sum())
    effects: dict[str, float] = {}

    for channel in CHANNELS:
        removal_probability = conversion_absorption_probability(
            remove_channel_from_transitions(transitions, channel)
        )
        effects[channel] = max(0.0, baseline_probability - removal_probability)

    total_effect = sum(effects.values())
    if total_effect <= 0:
        return linear_attribution(journeys)
    return {
        channel: total_revenue * effect / total_effect
        for channel, effect in effects.items()
    }


def attribution_summary(journeys: pd.DataFrame) -> pd.DataFrame:
    total_revenue = float(journeys.loc[journeys["converted"] == 1, "revenue"].sum())
    methods = {
        "First touch": first_touch_attribution(journeys),
        "Last touch": last_touch_attribution(journeys),
        "Linear": linear_attribution(journeys),
        "Markov removal": markov_removal_attribution(journeys),
    }
    rows = []
    for method, credits in methods.items():
        for channel in CHANNELS:
            credit_value = float(credits.get(channel, 0.0))
            rows.append(
                {
                    "method": method,
                    "channel": channel,
                    "credit_value": credit_value,
                    "credit_share": credit_value / total_revenue if total_revenue else 0.0,
                }
            )
    return pd.DataFrame(rows)


def method_share_table(summary: pd.DataFrame) -> pd.DataFrame:
    return summary.pivot(index="channel", columns="method", values="credit_share").reset_index()
