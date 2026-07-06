-- DuckDB views over the included Criteo-derived project sample and outputs.

CREATE OR REPLACE VIEW touchpoints AS
SELECT
    user_id,
    journey_id,
    touchpoint_id,
    touchpoint_sequence::INTEGER AS touchpoint_sequence,
    CAST(touchpoint_date AS DATE) AS touchpoint_date,
    source_day_int::INTEGER AS source_day_int,
    channel,
    channel_stage,
    converted::INTEGER AS converted,
    TRY_CAST(conversion_date AS DATE) AS conversion_date,
    sales_count::DOUBLE AS sales_count,
    revenue::DOUBLE AS revenue,
    is_clicked::INTEGER AS is_clicked,
    is_click_landed::INTEGER AS is_click_landed,
    source_campaign_id,
    source_publisher_id
FROM read_csv_auto('data/processed/criteo_touchpoints_sample.csv', HEADER = TRUE);

CREATE OR REPLACE VIEW v_fact_touchpoints AS
SELECT *
FROM touchpoints;

CREATE OR REPLACE VIEW v_journey_summary AS
SELECT *
FROM read_csv_auto('outputs/journey_summary.csv', HEADER = TRUE);
