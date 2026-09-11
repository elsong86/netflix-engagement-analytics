"""
One-time setup: load the analysis-ready CSV and the quarterly financials
CSV into a persistent DuckDB database file. Run this once (or again after
re-running the pipeline upstream); all subsequent analysis happens in SQL
against this database, not in pandas.
"""

import duckdb

con = duckdb.connect("netflix.duckdb")

con.execute("""
    CREATE OR REPLACE TABLE titles AS
    SELECT * FROM read_csv_auto('netflix_engagement_analysis_ready.csv')
""")
titles_count = con.execute("SELECT COUNT(*) FROM titles").fetchone()[0]
print(f"Loaded {titles_count} rows into netflix.duckdb (table: titles)")

con.execute("""
    CREATE OR REPLACE TABLE quarterly_financials AS
    SELECT * FROM read_csv_auto('netflix_quarterly_financials.csv')
""")
financials_count = con.execute("SELECT COUNT(*) FROM quarterly_financials").fetchone()[0]
print(f"Loaded {financials_count} rows into netflix.duckdb (table: quarterly_financials)")

con.close()