# Marketing Channel Attribution & Budget ROI Analysis

Portfolio project by Shalom Wu (GitHub: @shalom-wu)

This repo analyzes how different marketing attribution methods change budget decisions for a mid-size e-commerce business. The important business point is simple: last-touch attribution is convenient, but it can send money toward channels that close demand while underfunding channels that helped create it.

## Data Note

This project uses a clearly labeled synthetic multi-touch attribution dataset generated inside the repo. I looked for a clean, well-documented public dataset with user-level journeys, touchpoint dates, marketing channels, and conversion outcomes; for this build, I did not select one that was both accessible and sufficiently documented. The synthetic data is not real customer data and should not be presented as real performance.

## Key Findings

- **15,000 customer journeys and 47,308 touchpoints** were generated for January to early April 2026, with a **12.7% journey conversion rate** and **3.15 average touches per journey**.
- **Last-touch materially changes channel credit.** Paid Search receives **26.0%** of revenue credit under last-touch vs. **18.0%** under Markov removal; Display receives **4.2%** under last-touch vs. **11.6%** under Markov.
- **The estimated cost of using last-touch as the budget guide is $37.8K**, or **21.7%** of the synthetic quarter's $174K budget, versus a Markov-informed allocation.
- **Recommended scenario: balanced reallocation.** Shift **$19.6K** toward the Markov-informed mix for an estimated **$21.9K revenue lift**, **6.4% uplift**, and **1.12x incremental ROAS** under the documented response-curve assumption.

## Why This Matters

Most naive attribution work stops at "which channel gets credit?" This project connects attribution to the actual operating decision: where a marketing team should move budget, and what tradeoff it is accepting. The recommendation is deliberately not "trust the model blindly." It is a staged reallocation with a causal caveat and a recommendation to validate with incrementality testing.

## Methodology

1. **Synthetic journey generation:** one row per marketing touchpoint with `user_id`, `journey_id`, `touchpoint_date`, `channel`, conversion outcome, and synthetic revenue.
2. **EDA:** channel touch frequency, exposure conversion rates, average journey length, and common journey paths.
3. **Naive baselines:** first-touch, last-touch, and linear attribution.
4. **Data-driven attribution:** Markov chain removal-effect attribution, measuring how modeled conversion probability changes when a channel is removed from the transition graph.
5. **Budget strategy:** compare current synthetic budget, last-touch allocation, and Markov-informed allocation; then estimate staged reallocation scenarios with a diminishing-returns response curve.

## Repo Structure

| Path | Purpose |
|---|---|
| `data-sources.md` | Synthetic data source and generation methodology |
| `data/synthetic/customer_journeys.csv` | Generated touchpoint-level dataset |
| `src/attribution_roi/` | Data generation, attribution, budget, reporting, and visualization code |
| `scripts/` | One-command scripts for generation, analysis, deck, and notebook |
| `outputs/` | Analysis tables and model outputs |
| `reports/` | Executive summary, strategy deck, and presentation visuals |
| `notebooks/` | Reproducible notebook companion |
| `tests/` | Unit tests for generation, attribution, and budget logic |
| `explainer-guide/` | Plain-English guide for non-technical readers |

## Reproduce The Project

```bash
pip install -r requirements.txt
python scripts/run_all.py
pytest
```

The pipeline regenerates the synthetic dataset, analysis tables, visuals, summary report, markdown strategy deck, and notebook.

## Main Outputs

- Strategy deck: `reports/strategy_deck.md`
- Executive report: `reports/summary.md`
- Beginner explainer: `explainer-guide/explain-it-to-me.md`
- Attribution table: `outputs/attribution_summary.csv`
- Budget scenarios: `outputs/scenario_summary.csv`

## Limitations

- **Synthetic data:** this is a portfolio dataset calibrated to realistic attribution patterns, not a real company's data.
- **Correlational attribution:** Markov removal uses observed journey paths; it does not prove causal incrementality.
- **Budget response assumption:** scenario ROI depends on a simplified diminishing-returns curve, not a measured media response model.
- **Missing real economics:** a production business case should use contribution margin, customer lifetime value, returns, discounts, media fees, and channel saturation.

## License

MIT License. Copyright (c) 2026 Shalom Wu.
