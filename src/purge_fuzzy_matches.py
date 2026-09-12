"""
One-off cleanup: remove 'fuzzy' AND 'no_match' show rows from the cache so
they get reprocessed now that the year filter is no longer wrongly applied
to TV show searches. 'exact' rows and all movie rows are untouched.
"""

import pandas as pd

CACHE_FILE = "tmdb_enrichment_cache.csv"

df = pd.read_csv(CACHE_FILE)
before = len(df)

is_show = df["content_type"] == "show"
is_contaminated_status = df["match_status"].isin(["fuzzy", "no_match"])
to_remove = is_show & is_contaminated_status

removed_count = to_remove.sum()
df = df[~to_remove]

df.to_csv(CACHE_FILE, index=False)

print(f"Removed {removed_count} show rows (fuzzy or no_match) out of {before} total.")
print(f"Remaining in cache: {len(df)}")
print("These will be reprocessed without the year filter on the next enrich_tmdb.py run.")