-- Cross-tab: how much engagement comes from genuinely new content vs.
-- catalog content, and how much of the "new" bucket is actually a new
-- season of something already established vs. truly new/standalone.

SELECT
    release_bucket,
    is_returning_franchise,
    COUNT(*) AS title_count,
    SUM(hours_viewed) AS total_hours_viewed,
    AVG(hours_viewed) AS avg_hours_viewed_per_title
FROM titles
GROUP BY release_bucket, is_returning_franchise
ORDER BY release_bucket, is_returning_franchise;