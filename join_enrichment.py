"""
Join the TMDB enrichment cache onto the cleaned Netflix staging table,
producing the final analysis-ready dataset.

Input:  netflix_engagement_staging.csv
        tmdb_enrichment_cache.csv
Output: netflix_engagement_final.csv
"""

import pandas as pd

STAGING_FILE = "netflix_engagement_staging.csv"
CACHE_FILE = "tmdb_enrichment_cache.csv"
OUTPUT_FILE = "netflix_engagement_final.csv"

FINAL_STATUSES = {"exact", "fuzzy", "no_match"}


def main():
    staging = pd.read_csv(STAGING_FILE)
    cache = pd.read_csv(CACHE_FILE)

    # A title may appear more than once in the cache if an earlier run
    # failed (search_failed/details_failed) and a later run resolved it.
    # Keep only final-status rows, then drop_duplicates keeping the LAST
    # occurrence -- later rows in the file are from later (more complete)
    # runs, so "last" reflects the most recent resolution.
    cache = cache[cache["match_status"].isin(FINAL_STATUSES)]
    cache = cache.drop_duplicates(subset=["title", "content_type"], keep="last")

    before = len(staging)
    final = staging.merge(cache, on=["title", "content_type"], how="left")
    after = len(final)

    print(f"Staging rows: {before}")
    print(f"Rows after join: {after}")
    if before != after:
        print("  [warn] Row count changed after join -- check for duplicate keys in the cache.")

    print(f"\nMatch status breakdown:\n{final['match_status'].value_counts(dropna=False)}")

    final.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved final dataset to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()