import pandas as pd
import re

SOURCE_FILE = "data/raw/Netflix-s_What_We_Watched_Report_2026Jan-Jun__1_.xlsx"
OUTPUT_FILE = "data/processed/netflix_engagement_staging.csv"

# Real headers live on row 6 (1-indexed) -> header=5 in pandas (0-indexed)
HEADER_ROW = 5

# Rows to exclude outright -- these are report-level aggregates, not titles
AGGREGATE_ROW_TITLES = {"Other Shows", "Other Movies"}


def parse_runtime_to_minutes(value):
    """
    Runtime arrives as 'h:mm' text (e.g. '4:22' -> 4h 22m).
    Aggregate/footer rows store '*' instead -- return None, not 0,
    so it's clearly missing rather than falsely zero.
    """
    if value is None:
        return None
    value = str(value).strip()
    if value in ("*", "", "nan", "None"):
        return None
    match = re.match(r"^(\d+):(\d{2})$", value)
    if not match:
        return None  # unexpected format -- surfaced in the QA check below, not silently coerced
    hours, minutes = match.groups()
    return int(hours) * 60 + int(minutes)


def load_sheet(sheet_name, content_type):
    df = pd.read_excel(SOURCE_FILE, sheet_name=sheet_name, header=HEADER_ROW)
    df = df.dropna(subset="Title")
    df = df[~((df["Title"] == "Other Shows") | (df["Title"] == "Other Movies"))]
    df = df[~df["Title"].astype(str).str.startswith("*")]
    df["content_type"] = content_type
    return df


def main():
    shows = load_sheet("Shows", "show")
    movies = load_sheet("Movies", "movie")

    combined = pd.concat([shows, movies], ignore_index=True)

    # --- Type conversions ---
    combined["runtime_min"] = combined["Runtime"].apply(parse_runtime_to_minutes)

    # Release Date: some rows are genuinely missing (confirmed in Movies sheet --
    # a handful of titles, non-Latin script, have no Release Date at all, not '*').
    # Coerce errors to NaT rather than crashing, and track how many so it's a known
    # quantity, not a silent loss.
    combined["release_date"] = pd.to_datetime(combined["Release Date"], errors="coerce")

    combined["available_globally"] = combined["Available Globally?"].map(
        {"Yes": True, "No": False}
    )

    combined = combined.rename(
        columns={
            "Title": "title",
            "Hours Viewed": "hours_viewed",
            "Views": "views",
        }
    )

    # Derived metric: a rough "completion proxy" -- views * runtime approximates
    # hours viewed if everyone watched start to finish; hours_viewed / that
    # theoretical max gives a rough re-watch/completion signal.
    # Guard the zero/NaN runtime case explicitly rather than letting it silently
    # produce inf or NaN downstream.
    combined["completion_proxy"] = combined.apply(
        lambda row: row["hours_viewed"] / (row["views"] * row["runtime_min"] / 60)
        if pd.notna(row["runtime_min"]) and row["runtime_min"] > 0 and row["views"] > 0
        else None,
        axis=1,
    )

    final_cols = [
        "title",
        "content_type",
        "available_globally",
        "release_date",
        "hours_viewed",
        "runtime_min",
        "views",
        "completion_proxy",
    ]
    combined = combined[final_cols]

    # --- QA / sanity checks, printed so issues surface now, not downstream ---
    print(f"Total rows after cleaning: {len(combined)}")
    print(f"  Shows: {(combined['content_type'] == 'show').sum()}")
    print(f"  Movies: {(combined['content_type'] == 'movie').sum()}")
    print(f"Rows with missing runtime_min: {combined['runtime_min'].isna().sum()}")
    print(f"Rows with missing release_date: {combined['release_date'].isna().sum()}")
    print(f"Duplicate (title, content_type) pairs: "
          f"{combined.duplicated(subset=['title', 'content_type']).sum()}")

    combined.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved staging table to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()