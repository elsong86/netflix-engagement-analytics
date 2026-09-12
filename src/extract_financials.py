"""
Extract quarterly financial metrics directly from Netflix's official
investor-relations workbook (Q2-26-Website-Financials.xlsx). This file's
Income Statement and Cashflow sheets already contain every quarter back
through Q1'25 plus Q2'26 -- the Q1 workbook is a strict subset, so it's
not needed separately.

Row/column positions below were identified by inspecting this specific
workbook's layout directly (a static, published report -- not expected
to change), rather than generic label-matching, which is more fragile
against this report's inconsistent label indentation.

Output: netflix_quarterly_financials.csv
"""

import pandas as pd

SOURCE_FILE = "data/raw/Q2-26-Website-Financials.xlsx"
OUTPUT_FILE = "data/processed/netflix_quarterly_financials.csv"

QUARTER_LABELS = ["Q1'25", "Q2'25", "Q3'25", "Q4'25", "Q1'26", "Q2'26"]

# 0-indexed row positions within each sheet (row N in the printed view = iloc N-1)
INCOME_ROWS = {
    "revenue": 8,           # "Revenues"
    "operating_income": 13,  # "Operating income"
    "net_income": 19,        # "Net income"
    "diluted_eps": 22,       # "Diluted" (under Earnings per share)
}
# 0-indexed column positions for the 6 real quarters (skipping the
# "Twelve Months Ended" FY2025 column and the "Six Months Ended" H1'26
# column, since those aren't discrete quarters)
INCOME_COLS = [4, 5, 6, 7, 9, 10]

CASHFLOW_ROWS = {
    "net_cash_from_ops": 25,   # "Net cash provided by operating activities"
    "free_cash_flow": 49,      # "Non-GAAP free cash flow"
}
CASHFLOW_COLS = [7, 8, 9, 10, 12, 13]


def extract_row(sheet_df, row_idx, col_idxs):
    return [sheet_df.iloc[row_idx, c] for c in col_idxs]


def main():
    income = pd.read_excel(SOURCE_FILE, sheet_name="Income Statement", header=None)
    cashflow = pd.read_excel(SOURCE_FILE, sheet_name="Cashflow", header=None)

    data = {"quarter": QUARTER_LABELS}

    for field, row_idx in INCOME_ROWS.items():
        data[field] = extract_row(income, row_idx, INCOME_COLS)

    for field, row_idx in CASHFLOW_ROWS.items():
        data[field] = extract_row(cashflow, row_idx, CASHFLOW_COLS)

    df = pd.DataFrame(data)

    # Figures in the source are in thousands (per the sheet's own header note)
    for col in ["revenue", "operating_income", "net_income", "net_cash_from_ops", "free_cash_flow"]:
        df[col] = df[col] * 1000

    df["operating_margin_pct"] = (df["operating_income"] / df["revenue"] * 100).round(1)

    print(df.to_string(index=False))

    df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()