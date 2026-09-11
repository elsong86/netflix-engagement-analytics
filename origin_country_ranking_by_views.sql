-- Same ranking as origin_country_ranking.sql, but using VIEWS instead of
-- HOURS VIEWED. Netflix defines Views = Hours Viewed / Runtime, so this
-- metric is runtime-normalized by construction -- a long-running
-- telenovela season and a tight 10-episode drama season contribute
-- comparably per completed watch-through, rather than the telenovela
-- racking up more hours purely from having more total content to watch.
--
-- Comparing this ranking against the Hours Viewed version tests whether
-- a country's lead reflects genuine audience engagement or is partly a
-- byproduct of typical content length/format in that country's catalog.

WITH matched_titles AS (
    SELECT
        title,
        views,
        TRIM(SPLIT_PART(origin_country, ';', 1)) AS primary_origin_country
    FROM titles
    WHERE match_status IN ('exact', 'fuzzy')
      AND origin_country IS NOT NULL
      AND origin_country != ''
)

SELECT
    primary_origin_country,
    COUNT(*) AS title_count,
    SUM(views) AS total_views,
    AVG(views) AS avg_views_per_title
FROM matched_titles
GROUP BY primary_origin_country
HAVING COUNT(*) >= 15
ORDER BY avg_views_per_title DESC;