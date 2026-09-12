"""
Run a .sql file against netflix.duckdb and print the results.

Usage:
    python run_sql.py origin_country_ranking.sql
    python run_sql.py release_bucket_crosstab.sql
"""

import sys
import duckdb

if len(sys.argv) != 2:
    print("Usage: python run_sql.py <path_to_sql_file>")
    sys.exit(1)

sql_file = sys.argv[1]

with open(sql_file, "r") as f:
    query = f.read()

con = duckdb.connect("data/processed/netflix.duckdb")
result = con.execute(query).fetchdf()
con.close()

print(result.to_string(index=False))