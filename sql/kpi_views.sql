-- SQL reference views for marketing attribution and budget decision support.

CREATE OR REPLACE VIEW v_touchpoint_summary AS
SELECT *
FROM read_csv_auto('outputs/touchpoint_summary.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_attribution_summary AS
SELECT *
FROM read_csv_auto('outputs/attribution_summary.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_budget_reallocation AS
SELECT *
FROM read_csv_auto('outputs/budget_reallocation.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_scenario_summary AS
SELECT *
FROM read_csv_auto('outputs/scenario_summary.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_journey_patterns AS
SELECT *
FROM read_csv_auto('outputs/journey_patterns.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_channel_funnel AS
SELECT
    channel,
    COUNT(*) AS touchpoints,
    COUNT(DISTINCT journey_id) AS journeys_seen,
    COUNT(DISTINCT CASE WHEN converted = 1 THEN journey_id END) AS converted_journeys_seen,
    ROUND(COUNT(DISTINCT CASE WHEN converted = 1 THEN journey_id END)::DOUBLE / NULLIF(COUNT(DISTINCT journey_id), 0), 4) AS conversion_rate_when_seen,
    ROUND(SUM(is_clicked)::DOUBLE / NULLIF(COUNT(*), 0), 4) AS click_rate,
    ROUND(SUM(is_click_landed)::DOUBLE / NULLIF(SUM(is_clicked), 0), 4) AS landed_click_rate
FROM touchpoints
GROUP BY 1
ORDER BY touchpoints DESC;

CREATE OR REPLACE VIEW v_attribution_method_gap AS
SELECT
    channel,
    MAX(CASE WHEN method = 'Last touch' THEN credit_share END) AS last_touch_share,
    MAX(CASE WHEN method = 'Markov removal' THEN credit_share END) AS markov_share,
    ROUND(
        MAX(CASE WHEN method = 'Markov removal' THEN credit_share END)
        - MAX(CASE WHEN method = 'Last touch' THEN credit_share END),
        4
    ) AS markov_minus_last_touch_share
FROM v_attribution_summary
GROUP BY 1
ORDER BY ABS(markov_minus_last_touch_share) DESC;
