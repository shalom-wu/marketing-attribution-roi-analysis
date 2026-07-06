-- Checks for journey grain, channel coverage and output consistency.

SELECT '01 touchpoint rows' AS check_name, COUNT(*)::VARCHAR AS result
FROM touchpoints;

SELECT '02 journey count' AS check_name, COUNT(DISTINCT journey_id)::VARCHAR AS result
FROM touchpoints;

SELECT '03 channel count' AS check_name, COUNT(DISTINCT channel)::VARCHAR AS result
FROM touchpoints;

SELECT '04 duplicate touchpoint ids' AS check_name,
       COUNT(*)::VARCHAR AS result
FROM (
    SELECT touchpoint_id
    FROM touchpoints
    GROUP BY 1
    HAVING COUNT(*) > 1
);

SELECT '05 converted journeys' AS check_name,
       COUNT(DISTINCT CASE WHEN converted = 1 THEN journey_id END)::VARCHAR AS result
FROM touchpoints;

SELECT '06 missing channel labels' AS check_name,
       COUNT(*)::VARCHAR AS result
FROM touchpoints
WHERE channel IS NULL OR channel = '';

SELECT '07 source sample is derived from CriteoPrivateAd' AS check_name,
       'documented in data-sources.md and data/data_manifest.md' AS result;
