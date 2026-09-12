"""
Enrich the Netflix engagement staging table with genre, origin_country,
and original_language pulled from TMDB.

Input:  netflix_engagement_staging.csv   (from clean_netflix_engagement.py)
Output: tmdb_enrichment_cache.csv        (lookup table -- NOT merged into
                                           the staging file here; that join
                                           happens as a separate later step)

Design notes:
- The cache is checked BEFORE every API call. Already-resolved (title,
  content_type) pairs are skipped entirely on rerun -- this makes the
  script safe to stop and restart without wasting API calls or losing work.
- Processed in chunks (BATCH_SIZE), writing to the cache after every chunk,
  not just at the very end.
- Requires TMDB_API_KEY as an environment variable 
"""

import os
import re
import time
import pandas as pd
import requests
from rapidfuzz import fuzz, process

# Matches trailing suffixes Netflix appends that TMDB titles don't have,
# e.g. "Bridgerton: Season 4" -> "Bridgerton", "His & Hers: Limited Series"
# -> "His & Hers", "Love Is Blind: S10: Ohio" -> "Love Is Blind".
# Lazy base group + backtracking handles multi-colon titles correctly --
# it tries the shortest base first and only accepts a split once the
# remainder fully matches one of these known suffix shapes.
SEASON_SUFFIX_PATTERN = re.compile(
    r"^(?P<base>.+?):\s*"
    r"(Season\s+\d+|Limited Series|Volume\s+\d+|Chapter\s+\d+|Part\s+\d+|S\d+.*)$",
    re.IGNORECASE,
)

# Some franchises (Stranger Things 2/3/4/5) get a trailing number with no
# colon at all. Heuristic, not guaranteed safe -- flagged in README as a
# known limitation. Only applied if the colon-based pattern didn't already
# match, and only strips 1-2 digit trailing numbers.
TRAILING_NUMBER_PATTERN = re.compile(r"^(?P<base>.{3,}?)\s+\d{1,2}$")

# Captures a trailing "(YYYY)" so it can be used as a search year hint
# and removed from the search query itself, e.g. "The Cleaning Lady (2022)".
TRAILING_YEAR_PATTERN = re.compile(r"^(?P<base>.+?)\s*\((?P<year>\d{4})\)$")


def clean_search_title(raw_title):
    """
    Derive the title to actually search TMDB with, plus a year hint if one
    was embedded in the title. Returns (search_title, year_hint).
    """
    # Drop any bilingual/alternate-language title after "//"
    primary = raw_title.split("//")[0].strip()

    season_match = SEASON_SUFFIX_PATTERN.match(primary)
    if season_match:
        primary = season_match.group("base").strip()
    else:
        trailing_num_match = TRAILING_NUMBER_PATTERN.match(primary)
        if trailing_num_match:
            primary = trailing_num_match.group("base").strip()

    year_hint = None
    year_match = TRAILING_YEAR_PATTERN.match(primary)
    if year_match:
        primary = year_match.group("base").strip()
        year_hint = int(year_match.group("year"))

    return primary, year_hint

STAGING_FILE = "data/processed/netflix_engagement_staging.csv"
CACHE_FILE = "data/processed/tmdb_enrichment_cache.csv"

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = os.environ.get("TMDB_API_KEY")

BATCH_SIZE = 200
REQUEST_DELAY_SECONDS = 0.3   # modest pacing between requests
FUZZY_MATCH_THRESHOLD = 85    # 0-100 scale; below this, treat as no_match

CACHE_COLUMNS = [
    "title", "content_type", "genres", "origin_country",
    "original_language", "match_status",
]


def require_api_key():
    if not API_KEY:
        raise RuntimeError(
            "TMDB_API_KEY environment variable is not set.\n"
            "Set it before running, e.g.:\n"
            "  export TMDB_API_KEY='your_key_here'   (macOS/Linux)\n"
            "  $env:TMDB_API_KEY='your_key_here'      (Windows PowerShell)"
        )


def load_cache():
    """
    Return (cache_df, resolved_keys). resolved_keys only includes rows with
    a FINAL outcome (exact / fuzzy / no_match) -- rows that failed due to a
    network error (search_failed / details_failed) are deliberately left
    out, so the next run retries them instead of treating a transient
    failure as a permanent answer.
    """
    if os.path.exists(CACHE_FILE):
        cache_df = pd.read_csv(CACHE_FILE)
    else:
        cache_df = pd.DataFrame(columns=CACHE_COLUMNS)

    FINAL_STATUSES = {"exact", "fuzzy", "no_match"}
    resolved_df = cache_df[cache_df["match_status"].isin(FINAL_STATUSES)]
    resolved_keys = set(zip(resolved_df["title"], resolved_df["content_type"]))
    return cache_df, resolved_keys


def append_to_cache(new_rows):
    """Append a batch of results to the cache CSV, writing a header only
    if the file doesn't exist yet."""
    new_df = pd.DataFrame(new_rows, columns=CACHE_COLUMNS)
    file_exists = os.path.exists(CACHE_FILE)
    new_df.to_csv(CACHE_FILE, mode="a", header=not file_exists, index=False)


def tmdb_search(title, content_type, year=None):
    """
    Search TMDB for a title. content_type is 'show' or 'movie'.
    Returns (results, request_failed). request_failed=True means a network
    error occurred -- distinct from a genuinely empty result list, so
    callers can avoid treating a transient failure as a real "no match."
    """
    endpoint = "search/tv" if content_type == "show" else "search/movie"
    params = {"api_key": API_KEY, "query": title}

    if year is not None:
        year_param = "first_air_date_year" if content_type == "show" else "year"
        params[year_param] = int(year)

    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=20)
        response.raise_for_status()
        return response.json().get("results", []), False
    except requests.exceptions.RequestException as e:
        print(f"  [warn] Search failed for '{title}': {e}")
        return [], True


def tmdb_details(tmdb_id, content_type):
    """
    Fetch genres, origin_country, original_language for a matched title.
    Returns (genres, origin_country, original_language, request_failed).
    """
    endpoint = "tv" if content_type == "show" else "movie"
    params = {"api_key": API_KEY}

    try:
        response = requests.get(f"{BASE_URL}/{endpoint}/{tmdb_id}", params=params, timeout=20)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"  [warn] Details fetch failed for id {tmdb_id}: {e}")
        return None, None, None, True

    genres = "; ".join(g["name"] for g in data.get("genres", []))

    if content_type == "show":
        origin_country = "; ".join(data.get("origin_country", []))
    else:
        origin_country = "; ".join(
            c["iso_3166_1"] for c in data.get("production_countries", [])
        )

    original_language = data.get("original_language")

    return genres, origin_country, original_language, False


def pick_best_match(title, results, content_type):
    """
    Return (tmdb_id, match_status) or (None, 'no_match').

    Fuzzy matching prefers the most POPULAR candidate among everything that
    clears the similarity threshold, not just the top text-similarity score.
    This guards against matching a low-popularity companion/aftershow entry
    that shares the franchise name (e.g. a "Bridgerton" talk special) over
    the actual flagship show.
    """
    if not results:
        return None, "no_match"

    result_key = "name" if content_type == "show" else "title"

    # Exact match first (case-insensitive)
    for r in results:
        candidate_title = r.get(result_key, "")
        if candidate_title.strip().lower() == title.strip().lower():
            return r["id"], "exact"

    # Fuzzy: score every candidate, keep those above threshold, then pick
    # the most popular among survivors rather than the single top text score.
    qualifying = []
    for r in results:
        candidate_title = r.get(result_key, "")
        score = fuzz.WRatio(title, candidate_title)
        if score >= FUZZY_MATCH_THRESHOLD:
            qualifying.append(r)

    if not qualifying:
        return None, "no_match"

    best = max(qualifying, key=lambda r: r.get("popularity", 0))
    return best["id"], "fuzzy"


def enrich_title(title, content_type, year):
    search_title, year_hint_from_title = clean_search_title(title)

    # Year filtering is only meaningful for movies. For TV shows, TMDB's
    # year filter matches against first_air_date_year -- the show's
    # ORIGINAL premiere year, not the year of any particular season. A
    # staging release_date reflecting "Season 4 dropped in 2026" would
    # wrongly exclude a show that actually first aired in 2020, so never
    # apply a year filter to show searches.
    if content_type == "show":
        effective_year = None
    else:
        effective_year = year if year is not None else year_hint_from_title

    results, search_failed = tmdb_search(search_title, content_type, year=effective_year)

    if search_failed:
        # Network error, not a genuine "TMDB has no such title" -- keep
        # this distinct so it gets retried on the next run instead of
        # being locked in as a false no_match forever.
        return {
            "title": title, "content_type": content_type,
            "genres": None, "origin_country": None, "original_language": None,
            "match_status": "search_failed",
        }

    tmdb_id, match_status = pick_best_match(search_title, results, content_type)

    if tmdb_id is None:
        return {
            "title": title, "content_type": content_type,
            "genres": None, "origin_country": None, "original_language": None,
            "match_status": match_status,
        }

    genres, origin_country, original_language, details_failed = tmdb_details(tmdb_id, content_type)

    if details_failed:
        return {
            "title": title, "content_type": content_type,
            "genres": None, "origin_country": None, "original_language": None,
            "match_status": "details_failed",
        }

    return {
        "title": title, "content_type": content_type,
        "genres": genres, "origin_country": origin_country,
        "original_language": original_language, "match_status": match_status,
    }


def main():
    require_api_key()

    staging = pd.read_csv(STAGING_FILE)
    unique_titles = staging[["title", "content_type", "release_date"]].drop_duplicates(
        subset=["title", "content_type"]
    )

    cache_df, resolved_keys = load_cache()
    print(f"Already resolved from a prior run: {len(resolved_keys)}")

    to_process = [
        row for row in unique_titles.itertuples(index=False)
        if (row.title, row.content_type) not in resolved_keys
    ]
    print(f"Remaining to process: {len(to_process)}")

    batch = []
    for i, row in enumerate(to_process, start=1):
        year = None
        if pd.notna(row.release_date):
            year = pd.to_datetime(row.release_date).year

        result = enrich_title(row.title, row.content_type, year)
        batch.append(result)

        time.sleep(REQUEST_DELAY_SECONDS)

        if len(batch) >= BATCH_SIZE:
            append_to_cache(batch)
            print(f"  Progress: {i}/{len(to_process)} -- wrote batch to cache")
            batch = []

    if batch:
        append_to_cache(batch)
        print(f"  Progress: {len(to_process)}/{len(to_process)} -- wrote final batch to cache")

    print("\nDone. Results are in", CACHE_FILE)


if __name__ == "__main__":
    main()