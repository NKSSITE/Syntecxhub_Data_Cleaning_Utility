"""
Data Cleaning Utility
----------------------
A reusable command-line tool that cleans a messy CSV/Excel dataset:

  1. Standardizes column names
  2. Fixes incorrect dtypes (numbers, dates)
  3. Detects and handles missing values (drop / fill / impute)
  4. Removes duplicate rows
  5. Writes the cleaned dataset + a plain-text cleaning log

Usage:
    python data_cleaner.py input.csv
    python data_cleaner.py input.xlsx --output cleaned.csv --missing fill
    python data_cleaner.py input.csv --missing impute --log my_log.txt

Missing-value strategies (--missing):
    drop     : drop any row containing a missing value
    fill     : fill numeric columns with 0, text columns with "Unknown"
    impute   : fill numeric columns with column median, text columns with mode
"""

import argparse
import re
import sys
import warnings
from pathlib import Path

import pandas as pd


class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.log = []

    # ---------- logging helper ----------
    def _log(self, message: str):
        self.log.append(message)

    # ---------- 1. standardize column names ----------
    def standardize_columns(self):
        original = list(self.df.columns)
        new_cols = []
        for col in original:
            clean = str(col).strip().lower()
            clean = re.sub(r"[^\w]+", "_", clean)   # non-alphanumeric -> underscore
            clean = re.sub(r"_+", "_", clean).strip("_")
            new_cols.append(clean)
        self.df.columns = new_cols
        changed = [f"'{o}' -> '{n}'" for o, n in zip(original, new_cols) if o != n]
        if changed:
            self._log(f"Standardized {len(changed)} column name(s): " + ", ".join(changed))
        else:
            self._log("Column names already standardized.")
        return self

    # ---------- 2. fix dtypes ----------
    def fix_dtypes(self):
        for col in self.df.columns:
            series = self.df[col]

            if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
                # try numeric conversion
                numeric_try = pd.to_numeric(
                    series.astype(str).str.replace(",", "", regex=False).str.strip(),
                    errors="coerce"
                )
                non_null_original = series.notna().sum()
                non_null_converted = numeric_try.notna().sum()

                if non_null_original > 0 and non_null_converted / non_null_original >= 0.8:
                    self.df[col] = numeric_try
                    self._log(f"Column '{col}': converted to numeric.")
                    continue

                # try date conversion (looks like a date column by name or content)
                looks_like_date = "date" in col.lower() or "time" in col.lower()
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    date_try = pd.to_datetime(series, errors="coerce", format="mixed")
                non_null_dates = date_try.notna().sum()

                if non_null_original > 0 and (
                    looks_like_date or non_null_dates / non_null_original >= 0.8
                ):
                    if non_null_dates > 0:
                        self.df[col] = date_try
                        self._log(f"Column '{col}': parsed as datetime.")
        return self

    # ---------- 3. handle missing values ----------
    def handle_missing(self, strategy="fill"):
        missing_counts = self.df.isna().sum()
        total_missing = int(missing_counts.sum())

        if total_missing == 0:
            self._log("No missing values detected.")
            return self

        details = ", ".join(
            f"'{c}': {n}" for c, n in missing_counts.items() if n > 0
        )
        self._log(f"Detected {total_missing} missing value(s) -> {details}")

        if strategy == "drop":
            before = len(self.df)
            self.df = self.df.dropna()
            self._log(f"Strategy 'drop': removed {before - len(self.df)} row(s) with missing values.")

        elif strategy == "fill":
            for col in self.df.columns:
                if self.df[col].isna().any():
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        self.df[col] = self.df[col].fillna(0)
                        self._log(f"Column '{col}': filled missing values with 0.")
                    elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                        self._log(f"Column '{col}': left missing dates as NaT (no safe default).")
                    else:
                        self.df[col] = self.df[col].fillna("Unknown")
                        self._log(f"Column '{col}': filled missing values with 'Unknown'.")

        elif strategy == "impute":
            for col in self.df.columns:
                if self.df[col].isna().any():
                    if pd.api.types.is_numeric_dtype(self.df[col]):
                        median_val = self.df[col].median()
                        self.df[col] = self.df[col].fillna(median_val)
                        self._log(f"Column '{col}': imputed missing values with median ({median_val}).")
                    elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                        self._log(f"Column '{col}': left missing dates as NaT (no safe default).")
                    else:
                        mode_series = self.df[col].mode()
                        mode_val = mode_series.iloc[0] if not mode_series.empty else "Unknown"
                        self.df[col] = self.df[col].fillna(mode_val)
                        self._log(f"Column '{col}': imputed missing values with mode ('{mode_val}').")
        else:
            raise ValueError(f"Unknown missing-value strategy: {strategy}")

        return self

    # ---------- 4. remove duplicates ----------
    def remove_duplicates(self):
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        if removed > 0:
            self._log(f"Removed {removed} duplicate row(s).")
        else:
            self._log("No duplicate rows found.")
        return self

    # ---------- run full pipeline ----------
    def clean(self, missing_strategy="fill"):
        self.standardize_columns()
        self.fix_dtypes()
        self.handle_missing(strategy=missing_strategy)
        self.remove_duplicates()
        return self.df, self.log


def load_data(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in (".xlsx", ".xls"):
        return pd.read_excel(path)
    return pd.read_csv(path)


def save_data(df: pd.DataFrame, path: Path):
    if path.suffix.lower() in (".xlsx", ".xls"):
        df.to_excel(path, index=False)
    else:
        df.to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser(description="Clean a messy CSV/Excel dataset.")
    parser.add_argument("input", help="Path to the input CSV or Excel file")
    parser.add_argument("--output", default=None, help="Path for the cleaned output file")
    parser.add_argument("--log", default=None, help="Path for the cleaning log file")
    parser.add_argument(
        "--missing",
        choices=["drop", "fill", "impute"],
        default="fill",
        help="Strategy for handling missing values (default: fill)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {input_path}")
        sys.exit(1)

    output_path = Path(args.output) if args.output else input_path.with_name(
        input_path.stem + "_cleaned" + input_path.suffix
    )
    log_path = Path(args.log) if args.log else input_path.with_name(
        input_path.stem + "_cleaning_log.txt"
    )

    print(f"Loading data from {input_path} ...")
    df = load_data(input_path)
    rows_before, cols_before = df.shape

    cleaner = DataCleaner(df)
    cleaned_df, log_entries = cleaner.clean(missing_strategy=args.missing)

    rows_after, cols_after = cleaned_df.shape

    save_data(cleaned_df, output_path)

    summary = [
        "=== Data Cleaning Log ===",
        f"Input file:  {input_path}",
        f"Output file: {output_path}",
        f"Missing-value strategy: {args.missing}",
        f"Shape before: {rows_before} rows x {cols_before} columns",
        f"Shape after:  {rows_after} rows x {cols_after} columns",
        "",
        "Steps performed:",
    ] + [f"  - {entry}" for entry in log_entries]

    log_text = "\n".join(summary)
    log_path.write_text(log_text)

    print(log_text)
    print(f"\nCleaned dataset saved to: {output_path}")
    print(f"Cleaning log saved to:    {log_path}")


if __name__ == "__main__":
    main()
