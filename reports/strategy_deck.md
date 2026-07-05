# Marketing Attribution & Budget ROI Strategy

CriteoPrivateAd sample analysis  
Prepared by Shalom Wu

---

## 1. The Problem

Last-touch attribution is simple, which is why teams use it. The issue is that budget decisions need more than the final touch.

- Last-touch gives all credit to the last observed placement.
- Earlier placements can matter even when they are not last.
- The real question is not "what touched the customer last?" It is "where should the next dollar go?"

---

## 2. What Changed

The biggest bucket is stable, but the smaller placements shift.

- `Long-tail placements`: 50.7% under last-touch vs. 51.3% under Markov.
- `Publisher 03`: 3.8% under last-touch vs. 5.6% under Markov.
- `Publisher 04`: 7.3% under last-touch vs. 4.1% under Markov.
- Sample size: 11,343 multi-touch journeys, 1.8% conversion rate.

![Attribution comparison](figures/attribution_model_comparison.png)

---

## 3. Cost Of The Status Quo

If last-touch drove the budget, about $8.1K would land in the wrong place relative to the Markov-informed mix.

- That is 4.7% of the assumed pilot budget.
- Biggest increase under Markov: Long-tail placements (+$51.2K).
- Biggest reduction under Markov: Publisher 03 (-$9.3K).

![Budget gap](figures/budget_gap_to_markov.png)

---

## 4. Reallocation Scenarios

I modeled three levels of change. The more aggressive the shift, the higher the estimated contribution lift, but the less comfortable I would be rolling it out without a test.

| Scenario | Estimated Lift | Incremental ROAS | Tradeoff |
|---|---:|---:|---|
| Conservative rebalance | $3.8K | 0.21x | Move partway toward Markov credit; lowest disruption. |
| Balanced reallocation | $6.5K | 0.20x | Meaningful shift while keeping channel mix diversified. |
| Aggressive Markov target | $9.2K | 0.18x | Fully align budget with Markov credit; highest execution risk. |

![Scenario lift](figures/scenario_revenue_lift.png)

---

## 5. Recommendation

Use the balanced scenario.

- Shift 65% of the gap between current spend and the Markov-informed mix.
- Expected assumed contribution lift: $6.5K, or 19.0%.
- Keep last-touch as a reporting view, not the main budget allocator.
- Validate with a holdout or incrementality test before scaling.

---

## 6. How I Would Roll It Out

1. Keep tracking stable for one quarter.
2. Show first-touch, last-touch, linear, and Markov side by side.
3. Move budget in stages, with guardrails on CPA, margin, and conversion volume.
4. Test the biggest proposed shifts before making them permanent.

---

## 7. Method Notes

- Data: processed CriteoPrivateAd sample.
- Grain: one display impression becomes one attribution touchpoint.
- Placement groups: top eight publishers shown separately; the rest grouped as Long-tail placements.
- Models: first-touch, last-touch, linear, and Markov removal.
- Budget layer: assumed pilot spend, assumed contribution per sale, and a simple diminishing-returns curve.

---

## 8. Limits

- Attribution is correlational, not causal.
- The source is real Criteo data, but the publisher names are anonymized.
- The repo uses one shard, not the full CriteoPrivateAd dataset.
- Real deployment would need actual spend, margin, LTV, saturation, and finance-approved contribution economics.
