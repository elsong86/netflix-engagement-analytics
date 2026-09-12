"""
Diagnostic pass on the final joined dataset. Doesn't modify anything --
just surfaces whether the year-filter bug that was found and fixed for shows,
might also be affecting movies, plus a general quality spot-check.
"""

import pandas as pd

df = pd.read_csv("data/processed/netflix_engagement_final.csv")

print("=== Match status by content_type ===")
print(df.groupby("content_type")["match_status"].value_counts())

print("\n=== Well-known movies that are suspiciously no_match ===")
# Titles a hiring manager would recognize instantly -- if any of these
# come back no_match, that's a strong signal of the same year-filter bug.
known_movies = [
    "Jurassic World", "Despicable Me 3", "Despicable Me 4",
    "The Super Mario Bros. Movie", "Anaconda", "Madagascar",
    "Paw Patrol: The Movie", "The Secret Life of Pets",
]
check = df[
    (df["content_type"] == "movie")
    & (df["title"].str.contains("|".join(known_movies), case=False, na=False, regex=True))
]
print(check[["title", "release_date", "match_status", "genres", "origin_country"]])

print("\n=== Fuzzy movie matches with a single, generic-looking genre ===")
# The earlier bug's tell was a lone genre like "Talk" -- same signature
# worth checking for on the movie side.
suspicious_genres = {"Talk", "Documentary", "News"}
fuzzy_movies = df[(df["content_type"] == "movie") & (df["match_status"] == "fuzzy")]
flagged = fuzzy_movies[
    fuzzy_movies["genres"].isin(suspicious_genres)
]
print(f"Flagged rows: {len(flagged)}")
print(flagged[["title", "release_date", "genres", "origin_country"]].head(20))

print("\n=== Random sample of 20 fuzzy matches (any content_type) for a general spot-check ===")
sample = df[df["match_status"] == "fuzzy"].sample(min(20, (df["match_status"] == "fuzzy").sum()), random_state=42)
print(sample[["title", "content_type", "genres", "origin_country", "original_language"]])