# DAX Measures

```DAX
Touchpoints = COUNTROWS(fact_touchpoints)

Journeys = DISTINCTCOUNT(fact_touchpoints[journey_id])

Converted Journeys =
CALCULATE(
    DISTINCTCOUNT(fact_touchpoints[journey_id]),
    fact_touchpoints[converted] = 1
)

Conversion Rate = DIVIDE([Converted Journeys], [Journeys])

Current Budget = SUM(budget_reallocation[current_budget])

Recommended Markov Budget = SUM(budget_reallocation[markov_recommended_budget])

Budget Gap to Markov = SUM(budget_reallocation[budget_gap_to_markov])

Estimated Revenue Lift = SUM(scenario_summary[estimated_revenue_lift])
```

Equivalent measure on `fact_journey_summary`:

```DAX
Converted Journeys = SUM(fact_journey_summary[converted])
```
