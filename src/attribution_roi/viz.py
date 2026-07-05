from __future__ import annotations

import textwrap
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

TOKENS = {
    "surface": "#FCFCFD",
    "panel": "#FFFFFF",
    "ink": "#1F2430",
    "muted": "#6F768A",
    "grid": "#E6E8F0",
    "axis": "#D7DBE7",
}

COLOR_FAMILIES = {
    "blue": {"xlight": "#EAF1FE", "light": "#CEDFFE", "base": "#A3BEFA", "mid": "#5477C4", "dark": "#2E4780"},
    "gold": {"xlight": "#FFF4C2", "light": "#FFEA8F", "base": "#FFE15B", "mid": "#B8A037", "dark": "#736422"},
    "orange": {"xlight": "#FFEDDE", "light": "#FFBDA1", "base": "#F0986E", "mid": "#CC6F47", "dark": "#804126"},
    "olive": {"xlight": "#D8ECBD", "light": "#BEEB96", "base": "#A3D576", "mid": "#71B436", "dark": "#386411"},
    "pink": {"xlight": "#FCDAD6", "light": "#F5BACC", "base": "#F390CA", "mid": "#BD569B", "dark": "#8A3A6F"},
}


def use_chart_theme() -> None:
    sns.set_theme(
        style="whitegrid",
        rc={
            "figure.facecolor": TOKENS["surface"],
            "figure.edgecolor": "none",
            "savefig.facecolor": TOKENS["surface"],
            "savefig.edgecolor": "none",
            "axes.facecolor": TOKENS["panel"],
            "axes.edgecolor": TOKENS["axis"],
            "axes.labelcolor": TOKENS["ink"],
            "grid.color": TOKENS["grid"],
            "grid.linewidth": 0.8,
            "font.family": "DejaVu Sans",
            "patch.linewidth": 1.0,
        },
    )


def add_chart_header(fig, ax, title: str, subtitle: str) -> None:
    title = textwrap.fill(title, width=82, break_long_words=False)
    subtitle = textwrap.fill(subtitle, width=118, break_long_words=False)
    ax.set_title("")
    fig.subplots_adjust(top=0.82)
    left = ax.get_position().x0
    fig.text(left, 0.975, title, ha="left", va="top", fontsize=13, fontweight="semibold", color=TOKENS["ink"])
    fig.text(left, 0.925, subtitle, ha="left", va="top", fontsize=9, color=TOKENS["muted"])
    sns.despine(ax=ax)


def _save(fig, output_dir: Path, name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_dir / f"{name}.png", dpi=180, bbox_inches="tight")
    fig.savefig(output_dir / f"{name}.svg", bbox_inches="tight")
    plt.close(fig)


def plot_touchpoint_frequency(touch_summary, output_dir: Path) -> None:
    use_chart_theme()
    plot_df = touch_summary.sort_values("touchpoints", ascending=True)
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    family = COLOR_FAMILIES["blue"]
    sns.barplot(
        data=plot_df,
        x="touchpoints",
        y="channel",
        color=family["base"],
        edgecolor=family["dark"],
        linewidth=1.0,
        ax=ax,
    )
    ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("Touchpoints")
    ax.set_ylabel("")
    add_chart_header(
        fig,
        ax,
        "Touchpoint volume by marketing channel",
        "Processed CriteoPrivateAd sample, one row per display impression touchpoint from day_int=1.",
    )
    _save(fig, output_dir, "touchpoint_frequency_by_channel")


def plot_conversion_rate_by_channel(touch_summary, output_dir: Path) -> None:
    use_chart_theme()
    plot_df = touch_summary.sort_values("conversion_rate_when_seen", ascending=True)
    fig, ax = plt.subplots(figsize=(9.5, 5.5))
    family = COLOR_FAMILIES["olive"]
    sns.barplot(
        data=plot_df,
        x="conversion_rate_when_seen",
        y="channel",
        color=family["base"],
        edgecolor=family["dark"],
        linewidth=1.0,
        ax=ax,
    )
    ax.xaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("Journey conversion rate when channel appeared")
    ax.set_ylabel("")
    add_chart_header(
        fig,
        ax,
        "Conversion rate by channel exposure",
        "Channel-level rates are journey exposure rates, not causal lift estimates.",
    )
    _save(fig, output_dir, "conversion_rate_by_channel")


def plot_journey_length_distribution(journeys, output_dir: Path) -> None:
    use_chart_theme()
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    family = COLOR_FAMILIES["gold"]
    sns.histplot(
        data=journeys,
        x="journey_length",
        bins=range(1, int(journeys["journey_length"].max()) + 2),
        color=family["base"],
        edgecolor=family["dark"],
        linewidth=1.0,
        ax=ax,
    )
    ax.set_xlabel("Touchpoints in journey")
    ax.set_ylabel("Journeys")
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:,.0f}"))
    add_chart_header(
        fig,
        ax,
        "Most journeys have multiple touches before outcome",
        "Average journey length matters because first-touch and last-touch models discard most observed interactions.",
    )
    _save(fig, output_dir, "journey_length_distribution")


def plot_attribution_comparison(attribution_summary, output_dir: Path) -> None:
    use_chart_theme()
    fig, ax = plt.subplots(figsize=(11, 6.2))
    method_order = ["First touch", "Last touch", "Linear", "Markov removal"]
    palette = {
        "First touch": COLOR_FAMILIES["blue"]["base"],
        "Last touch": COLOR_FAMILIES["orange"]["base"],
        "Linear": COLOR_FAMILIES["gold"]["base"],
        "Markov removal": COLOR_FAMILIES["olive"]["base"],
    }
    sns.barplot(
        data=attribution_summary,
        x="channel",
        y="credit_share",
        hue="method",
        hue_order=method_order,
        palette=palette,
        edgecolor=TOKENS["ink"],
        linewidth=0.7,
        ax=ax,
    )
    ax.yaxis.set_major_formatter(mticker.PercentFormatter(1.0))
    ax.set_xlabel("")
    ax.set_ylabel("Share of attributed contribution")
    ax.tick_params(axis="x", rotation=25)
    ax.legend(loc="lower left", bbox_to_anchor=(0, 1.01), frameon=False, ncol=4, borderaxespad=0)
    add_chart_header(
        fig,
        ax,
        "Attribution credit changes materially by model",
        "Shares allocate the same assumed contribution pool across first touch, last touch, linear, and Markov removal-effect methods.",
    )
    _save(fig, output_dir, "attribution_model_comparison")


def plot_budget_gap(budget, output_dir: Path) -> None:
    use_chart_theme()
    plot_df = budget.sort_values("budget_gap_to_markov")
    fig, ax = plt.subplots(figsize=(9.8, 5.8))
    positive = COLOR_FAMILIES["olive"]
    negative = COLOR_FAMILIES["orange"]
    colors = [positive["base"] if value >= 0 else negative["base"] for value in plot_df["budget_gap_to_markov"]]
    edges = [positive["dark"] if value >= 0 else negative["dark"] for value in plot_df["budget_gap_to_markov"]]
    bars = ax.barh(plot_df["channel"], plot_df["budget_gap_to_markov"], color=colors, edgecolor=edges, linewidth=1.0)
    ax.axvline(0, color=TOKENS["ink"], linewidth=1.0)
    min_gap = float(plot_df["budget_gap_to_markov"].min())
    max_gap = float(plot_df["budget_gap_to_markov"].max())
    label_offset = max((max_gap - min_gap) * 0.035, 1200)
    ax.set_xlim(min_gap - label_offset * 4.0, max_gap + label_offset * 4.0)
    for bar, value in zip(bars, plot_df["budget_gap_to_markov"]):
        label_x = value + (label_offset if value >= 0 else -label_offset)
        ax.text(
            label_x,
            bar.get_y() + bar.get_height() / 2,
            f"${value/1000:+.1f}K",
            ha="left" if value >= 0 else "right",
            va="center",
            fontsize=8,
            color=TOKENS["ink"],
        )
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}K"))
    ax.set_xlabel("Budget gap to Markov recommendation")
    ax.set_ylabel("")
    add_chart_header(
        fig,
        ax,
        "Budget shifts implied by Markov attribution",
        "Positive values are channels receiving more budget under the Markov-informed allocation; negative values are reductions.",
    )
    _save(fig, output_dir, "budget_gap_to_markov")


def plot_scenario_lift(scenarios, output_dir: Path) -> None:
    use_chart_theme()
    fig, ax = plt.subplots(figsize=(9, 5.2))
    family = COLOR_FAMILIES["pink"]
    sns.barplot(
        data=scenarios,
        x="scenario",
        y="estimated_revenue_lift",
        color=family["base"],
        edgecolor=family["dark"],
        linewidth=1.0,
        ax=ax,
    )
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1000:,.0f}K"))
    ax.set_xlabel("")
    ax.set_ylabel("Estimated contribution lift")
    ax.tick_params(axis="x", rotation=15)
    add_chart_header(
        fig,
        ax,
        "Reallocation scenarios show modest upside with execution risk",
        "Scenario estimates use a simple diminishing-returns response curve, so they should frame decisions rather than claim causality.",
    )
    _save(fig, output_dir, "scenario_revenue_lift")
