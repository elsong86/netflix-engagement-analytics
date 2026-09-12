(venv) ellissong@Elliss-Laptop netflix % python src/clean_netflix_engagement.py
python src/enrich_tmdb.py
python src/join_enrichment.py
python src/add_engagement_buckets.py
python src/extract_financials.py
python src/setup_duckdb.py
python src/run_sql.py sql/origin_country_ranking.sql
python src/export_for_tableau.py
Total rows after cleaning: 17370
  Shows: 8193
  Movies: 9177
Rows with missing runtime_min: 310
Rows with missing release_date: 11324
Duplicate (title, content_type) pairs: 3
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/clean_netflix_engagement.py", line 106, in <module>
    main()
    ~~~~^^
  File "/Users/ellissong/Projects/netflix/src/clean_netflix_engagement.py", line 101, in main
    combined.to_csv(OUTPUT_FILE, index=False)
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/core/generic.py", line 3976, in to_csv
    return DataFrameRenderer(formatter).to_csv(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        path_or_buf,
        ^^^^^^^^^^^^
    ...<14 lines>...
        storage_options=storage_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/formats/format.py", line 1025, in to_csv
    csv_formatter.save()
    ~~~~~~~~~~~~~~~~~~^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/formats/csvs.py", line 251, in save
    with get_handle(
         ~~~~~~~~~~^
        self.filepath_or_buffer,
        ^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        storage_options=self.storage_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ) as handles:
    ^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/common.py", line 797, in get_handle
    check_parent_directory(str(handle))
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/common.py", line 656, in check_parent_directory
    raise OSError(rf"Cannot save file into a non-existent directory: '{parent}'")
OSError: Cannot save file into a non-existent directory: 'data/processed'
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/enrich_tmdb.py", line 308, in <module>
    main()
    ~~~~^^
  File "/Users/ellissong/Projects/netflix/src/enrich_tmdb.py", line 268, in main
    require_api_key()
    ~~~~~~~~~~~~~~~^^
  File "/Users/ellissong/Projects/netflix/src/enrich_tmdb.py", line 91, in require_api_key
    raise RuntimeError(
    ...<4 lines>...
    )
RuntimeError: TMDB_API_KEY environment variable is not set.
Set it before running, e.g.:
  export TMDB_API_KEY='your_key_here'   (macOS/Linux)
  $env:TMDB_API_KEY='your_key_here'      (Windows PowerShell)
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/join_enrichment.py", line 47, in <module>
    main()
    ~~~~^^
  File "/Users/ellissong/Projects/netflix/src/join_enrichment.py", line 20, in main
    staging = pd.read_csv(STAGING_FILE)
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 873, in read_csv
    return _read(filepath_or_buffer, kwds)
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 300, in _read
    parser = TextFileReader(filepath_or_buffer, **kwds)
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1645, in __init__
    self._engine = self._make_engine(f, self.engine)
                   ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1904, in _make_engine
    self.handles = get_handle(
                   ~~~~~~~~~~^
        f,
        ^^
    ...<6 lines>...
        storage_options=self.options.get("storage_options", None),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/common.py", line 930, in get_handle
    handle = open(
        handle,
    ...<3 lines>...
        newline="",
    )
FileNotFoundError: [Errno 2] No such file or directory: 'data/processed/netflix_engagement_staging.csv'
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/add_engagement_buckets.py", line 82, in <module>
    main()
    ~~~~^^
  File "/Users/ellissong/Projects/netflix/src/add_engagement_buckets.py", line 58, in main
    df = pd.read_csv(INPUT_FILE)
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 873, in read_csv
    return _read(filepath_or_buffer, kwds)
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 300, in _read
    parser = TextFileReader(filepath_or_buffer, **kwds)
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1645, in __init__
    self._engine = self._make_engine(f, self.engine)
                   ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/parsers/readers.py", line 1904, in _make_engine
    self.handles = get_handle(
                   ~~~~~~~~~~^
        f,
        ^^
    ...<6 lines>...
        storage_options=self.options.get("storage_options", None),
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/common.py", line 930, in get_handle
    handle = open(
        handle,
    ...<3 lines>...
        newline="",
    )
FileNotFoundError: [Errno 2] No such file or directory: 'data/processed/netflix_engagement_final.csv'
quarter     revenue  operating_income  net_income  diluted_eps  net_cash_from_ops  free_cash_flow  operating_margin_pct
  Q1'25 10542801000        3346999000  2890351000         0.66         2789199000      2660922000                  31.7
  Q2'25 11079166000        3774694000  3125413000         0.72         2423258000      2267369000                  34.1
  Q3'25 11510307000        3248247000  2546916000         0.59         2825174000      2660455000                  28.2
  Q4'25 12050762000        2956663000  2418521000         0.56         2111642000      1872307000                  24.5
  Q1'26 12249757000        3956997000  5282791000         1.23         5290205000      5094075000                  32.3
  Q2'26 12559938000        4192610000  3401414000         0.80         1743812000      1525168000                  33.4
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/extract_financials.py", line 73, in <module>
    main()
    ~~~~^^
  File "/Users/ellissong/Projects/netflix/src/extract_financials.py", line 68, in main
    df.to_csv(OUTPUT_FILE, index=False)
    ~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/core/generic.py", line 3976, in to_csv
    return DataFrameRenderer(formatter).to_csv(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        path_or_buf,
        ^^^^^^^^^^^^
    ...<14 lines>...
        storage_options=storage_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/formats/format.py", line 1025, in to_csv
    csv_formatter.save()
    ~~~~~~~~~~~~~~~~~~^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/formats/csvs.py", line 251, in save
    with get_handle(
         ~~~~~~~~~~^
        self.filepath_or_buffer,
        ^^^^^^^^^^^^^^^^^^^^^^^^
    ...<4 lines>...
        storage_options=self.storage_options,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ) as handles:
    ^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/common.py", line 797, in get_handle
    check_parent_directory(str(handle))
    ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^
  File "/Users/ellissong/Projects/netflix/venv/lib/python3.14/site-packages/pandas/io/common.py", line 656, in check_parent_directory
    raise OSError(rf"Cannot save file into a non-existent directory: '{parent}'")
OSError: Cannot save file into a non-existent directory: 'data/processed'
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/setup_duckdb.py", line 10, in <module>
    con = duckdb.connect("data/processed/netflix.duckdb")
_duckdb.IOException: IO Error: Cannot open file "/Users/ellissong/Projects/netflix/data/processed/netflix.duckdb": No such file or directory
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/run_sql.py", line 21, in <module>
    con = duckdb.connect("data/processed/netflix.duckdb")
_duckdb.IOException: IO Error: Cannot open file "/Users/ellissong/Projects/netflix/data/processed/netflix.duckdb": No such file or directory
Traceback (most recent call last):
  File "/Users/ellissong/Projects/netflix/src/export_for_tableau.py", line 36, in <module>
    con = duckdb.connect("data/processed/netflix.duckdb")
_duckdb.IOException: IO Error: Cannot open file "/Users/ellissong/Projects/netflix/data/processed/netflix.duckdb": No such file or directory
(venv) ellissong@Elliss-Laptop netflix % 