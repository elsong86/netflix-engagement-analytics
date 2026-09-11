"""
Export data out of netflix.duckdb as CSVs for Tableau Public.

Tableau Public can't connect to DuckDB directly (no custom/JDBC connector
support in web authoring) -- it only reads Excel, Google Drive, OData, or
plain text files. This script is the bridge: the real analysis lives in
SQL against netflix.duckdb, and this just materializes what Tableau needs
as CSVs.
"""

import duckdb
import pycountry

# A few ISO codes where pycountry's official name reads awkwardly for a
# dashboard ("Korea, Republic of", "Russian Federation"), plus a handful
# of non-standard/historical codes TMDB sometimes returns that aren't in
# the ISO 3166 list at all (e.g. former countries, disputed regions).
COUNTRY_NAME_OVERRIDES = {
    "RU": "Russia",
    "SU": "Soviet Union (historical)",
    "XC": "Czechoslovakia (historical)",
    "XG": "East Germany (historical)",
    "XK": "Kosovo",
}


def country_code_to_name(code):
    if code in COUNTRY_NAME_OVERRIDES:
        return COUNTRY_NAME_OVERRIDES[code]
    country = pycountry.countries.get(alpha_2=code)
    if country is None:
        return code  # unmapped/unrecognized code -- fall back to the raw code rather than erroring
    return getattr(country, "common_name", None) or country.name


con = duckdb.connect("netflix.duckdb")

# Full tables, for panels that need the raw title-level or quarterly detail
con.execute("COPY titles TO 'titles_export.csv' (HEADER, DELIMITER ',')")
con.execute("COPY quarterly_financials TO 'quarterly_financials_export.csv' (HEADER, DELIMITER ',')")

# Origin-country ranking: routed through pandas (rather than a direct
# DuckDB COPY, like the others) specifically to add the country_name
# column below.
with open("origin_country_ranking.sql") as f:
    query = f.read().strip().rstrip(";")
    hours_ranking_df = con.execute(query).fetchdf()

hours_ranking_df["country_name"] = hours_ranking_df["primary_origin_country"].apply(country_code_to_name)
hours_ranking_df.to_csv("origin_country_ranking_export.csv", index=False)

with open("origin_country_ranking_by_views.sql") as f:
    query = f.read().strip().rstrip(";")
    views_ranking_df = con.execute(query).fetchdf()

views_ranking_df["country_name"] = views_ranking_df["primary_origin_country"].apply(country_code_to_name)
views_ranking_df.to_csv("origin_country_ranking_by_views_export.csv", index=False)

with open("release_bucket_crosstab.sql") as f:
    query = f.read().strip().rstrip(";")
    con.execute(f"COPY ({query}) TO 'release_bucket_crosstab_export.csv' (HEADER, DELIMITER ',')")

con.close()

print("Exported: titles_export.csv, quarterly_financials_export.csv,")
print("          origin_country_ranking_export.csv (hours, with country_name),")
print("          origin_country_ranking_by_views_export.csv (views, with country_name),")
print("          release_bucket_crosstab_export.csv")