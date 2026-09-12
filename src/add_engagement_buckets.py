"""
Add analysis columns to the final enriched dataset:
  - release_bucket: new_release / catalog / unknown_release_date
  - season_number: parsed from the title, if detectable (e.g. "Season 4" -> 4)
  - is_returning_franchise: True if season_number > 1

Input:  netflix_engagement_final.csv
Output: netflix_engagement_analysis_ready.csv
"""

import re
import pandas as pd

INPUT_FILE = "data/processed/netflix_engagement_final.csv"
OUTPUT_FILE = "data/processed/netflix_engagement_analysis_ready.csv"

# The report covers Jan 1 - Jun 30, 2026. Anything with a release_date on
# or after this counts as "new" for this report period; anything earlier
# is catalog content being watched/rewatched during the window.
REPORT_START = pd.Timestamp("2026-01-01")

# Patterns to pull a season/part number out of the ORIGINAL title text
# (distinct from clean_search_title in enrich_tmdb.py -- that one strips
# the suffix for API searching; this one extracts the number for analysis).
SEASON_OR_S_PATTERN = re.compile(r":\s*(?:Season|S)\s*(\d+)", re.IGNORECASE)
PART_PATTERN = re.compile(r":\s*Part\s*(\d+)", re.IGNORECASE)
TRAILING_NUMBER_PATTERN = re.compile(r"\s(\d{1,2})$")


def extract_season_number(title):
    """Return an int season/part number if detectable in the title, else None."""
    primary = title.split("//")[0].strip()

    match = SEASON_OR_S_PATTERN.search(primary)
    if match:
        return int(match.group(1))

    match = PART_PATTERN.search(primary)
    if match:
        return int(match.group(1))

    match = TRAILING_NUMBER_PATTERN.search(primary)
    if match:
        return int(match.group(1))

    return None


def classify_release(release_date):
    if pd.isna(release_date):
        return "unknown_release_date"
    if pd.Timestamp(release_date) >= REPORT_START:
        return "new_release"
    return "catalog"


def main():
    df = pd.read_csv(INPUT_FILE)
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")

    df["release_bucket"] = df["release_date"].apply(classify_release)

    df["season_number"] = df["title"].apply(extract_season_number)
    df["is_returning_franchise"] = df["season_number"].apply(
        lambda n: n is not None and n > 1
    )

    print("=== release_bucket ===")
    print(df["release_bucket"].value_counts())

    print("\n=== is_returning_franchise ===")
    print(df["is_returning_franchise"].value_counts())

    print("\n=== Cross-tab: release_bucket x is_returning_franchise ===")
    print(pd.crosstab(df["release_bucket"], df["is_returning_franchise"]))

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()