-- Business-facing review queries for attribution and budget decisions.

SELECT *
FROM v_channel_funnel;

SELECT *
FROM v_attribution_method_gap;

SELECT *
FROM v_budget_reallocation
ORDER BY ABS(budget_gap_to_markov) DESC;

SELECT *
FROM v_scenario_summary;

SELECT *
FROM v_journey_patterns
ORDER BY journeys DESC
LIMIT 10;
