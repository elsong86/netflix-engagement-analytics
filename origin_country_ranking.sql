WITH matched_titles AS (
    SELECT title, hours_viewed, TRIM(SPLIT_PART(origin_country, ';', 1)) AS primary_origin_country
    FROM titles 
    WHERE match_status IN ('exact', 'fuzzy')
     AND origin_country IS NOT NULL 
     AND origin_country <> ''
)
SELECT 
    primary_origin_country, 
    COUNT(*) AS total_count, 
    SUM(hours_viewed) AS total_hours_viewed, 
    AVG(hours_viewed) AS avg_hours_viewed_per_title
FROM matched_titles
GROUP BY primary_origin_country
HAVING COUNT(*) >= 15
ORDER BY avg_hours_viewed_per_title DESC; 