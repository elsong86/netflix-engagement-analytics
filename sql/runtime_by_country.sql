-- Tests the hypothesis raised while investigating Colombia's Hours-vs-Views
-- divergence: are Colombian-origin SHOWS genuinely longer (more total
-- runtime per season) than the typical show elsewhere, which would help
-- explain high total hours viewed without proportionally high views?
--
-- Uses MEDIAN, not just AVG, since a handful of extremely long seasons
-- could skew an average even if most Colombian shows are fairly typical
-- length -- median is more robust to that kind of outlier.
--
-- content_type = 'show' only: this comparison is specifically about
-- season length/format, which doesn't apply to movies the same way.

SELECT
    primary_origin_country,
    COUNT(*) AS title_count,
    MEDIAN(runtime_min) AS median_runtime_min,
    AVG(runtime_min) AS avg_runtime_min
FROM (
    SELECT
        title,
        runtime_min,
        TRIM(SPLIT_PART(origin_country, ';', 1)) AS primary_origin_country
    FROM titles
    WHERE match_status IN ('exact', 'fuzzy')
      AND content_type = 'show'
      AND origin_country IS NOT NULL
      AND origin_country != ''
      AND runtime_min IS NOT NULL
)
GROUP BY primary_origin_country
HAVING COUNT(*) >= 15
ORDER BY median_runtime_min DESC;