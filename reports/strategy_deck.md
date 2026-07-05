# Marketing Channel Attribution & Budget ROI Strategy

Synthetic portfolio analysis for a mid-size e-commerce business  
Prepared by Shalom Wu

---

## 1. Problem Framing

Last-touch attribution is easy to explain but risky for budget decisions.

- It gives 100% credit to the final observed channel before conversion.
- That can over-credit demand-capture channels and under-credit channels that created the demand earlier.
- The business problem is not "which channel touched the customer last?" It is "where should the next budget dollar go?"

---

## 2. Key Finding

Attribution method choice materially changes channel credit.

- Markov removal gives Paid Search the highest credit at 18.0%.
- Last-touch credits the same channel at 26.0%.
- The synthetic dataset contains 15,000 journeys and a 12.7% conversion rate.

![Attribution comparison](figures/attribution_model_comparison.png)

---

## 3. Cost Of The Status Quo

Using last-touch as the budget guide would misallocate an estimated $37.8K.

- That equals 21.7% of the synthetic quarter budget.
- The biggest increase under Markov is Referral ($8.3K).
- The biggest reduction is Paid Search ($-23.6K).

![Budget gap](figures/budget_gap_to_markov.png)

---

## 4. Reallocation Scenarios

Three scenarios translate attribution into operating choices.

| Scenario | Estimated Lift | Incremental ROAS | Tradeoff |
|---|---:|---:|---|
| Conservative rebalance | $12.6K | 1.19x | Move partway toward Markov credit; lowest disruption. |
| Balanced reallocation | $21.9K | 1.12x | Meaningful shift while keeping channel mix diversified. |
| Aggressive Markov target | $31.2K | 1.04x | Fully align budget with Markov credit; highest execution risk. |

![Scenario lift](figures/scenario_revenue_lift.png)

---

## 5. Recommended Approach

Use a balanced reallocation, not a full swing to the model.

- Shift 65% of the gap between current spend and Markov-informed spend.
- Expected synthetic revenue lift: $21.9K, or 6.4%.
- Keep last-touch reporting for operational diagnostics, but do not use it as the primary budget allocator.
- Validate the recommendation with a holdout or incrementality test before scaling.

---

## 6. Deployment Strategy

1. Keep current tracking taxonomy stable for one quarter.
2. Report first-touch, last-touch, linear, and Markov credit side by side.
3. Move budget in staged increments with guardrails on CPA, margin, and conversion volume.
4. Use experiments to calibrate causal lift where the attribution model suggests material spend shifts.

---

## 7. Appendix: Methodology

- Dataset: deterministic synthetic customer journeys, clearly labeled as synthetic.
- Grain: one touchpoint row per user journey interaction.
- Baselines: first-touch, last-touch, and linear attribution.
- Data-driven model: Markov chain removal effect, which measures conversion-probability drop when a channel is removed from paths.
- Budget model: current-quarter spend assumption, Markov credit shares, and a diminishing-returns response curve.

---

## 8. Appendix: Limitations

- Attribution is correlational, not causal.
- Synthetic data cannot prove real-world performance.
- Channel costs, gross margin, customer lifetime value, and saturation would need real business inputs.
- Real deployment should reconcile attribution with incrementality tests, media-mix modeling, and finance-approved contribution economics.
