# Data Cleaning Utility

A simple, reusable Python command-line tool that cleans messy CSV/Excel datasets – handling missing values, incorrect data types, duplicates, and inconsistent column names — and outputs a cleaned file plus a plain-text cleaning log.

## Features

- Standardizes column names — converts headers to lowercase, snake_case (e.g. `"Full Name"` → `full_name`)
- Fixes incorrect dtypes — detects and converts numeric-looking text columns to numbers, and parses date columns automatically (handles mixed date formats safely)
- Handles missing values — choose one of three strategies:
  - `drop` — remove rows with missing values
  - `fill` — fill numeric columns with `0`, text columns with `"Unknown"`
  - `impute` — fill numeric columns with the median, text columns with the mode
- Removes duplicate rows
- Outputs: a cleaned dataset (same format as input) and a detailed cleaning log (`.txt`)

## Requirements

- Python 3.8+
- pandas
- openpyxl (only needed for Excel files)

Install dependencies:
```bash
pip install pandas openpyxl
```

## Usage

Basic usage (defaults to the `fill` strategy):
```bash
python data_cleaner.py your_file.csv
```

Specify a missing-value strategy:
```bash
python data_cleaner.py your_file.csv --missing impute
```

Custom output and log paths:
```bash
python data_cleaner.py your_file.xlsx --output cleaned.xlsx --log cleaning_log.txt
```

### Arguments

| Argument | Description | Default |
| `input` | Path to the input CSV or Excel file (required) | — |
| `--output` | Path for the cleaned output file | `<input>_cleaned.<ext>` |
| `--log` | Path for the cleaning log file | `<input>_cleaning_log.txt` |
| `--missing` | Missing-value strategy: `drop`, `fill`, or `impute` | `fill` |

## Example

A sample messy dataset (`sample_messy_data.csv`) is included, with mixed date formats, missing values, a duplicate row, and inconsistent column naming — useful for testing the tool.

```bash
python data_cleaner.py sample_messy_data.csv --missing impute
```

This produces:
- `sample_messy_data_cleaned.csv` — the cleaned dataset
- `sample_messy_data_cleaning_log.txt` — a log of every transformation applied

## How It Works

The tool is built around a `DataCleaner` class that runs through four steps in order:

1. `standardize_columns()` — normalizes column headers
2. `fix_dtypes()` — converts columns to numeric or datetime where appropriate
3. `handle_missing()` — applies the chosen missing-value strategy
4. `remove_duplicates()` — drops exact duplicate rows

Each step logs what it did, and the final log is written alongside the cleaned file so you can audit exactly what changed.

## Skills Demonstrated

- Data cleaning and preprocessing with pandas
- Handling missing data (drop/fill/impute strategies)
- Type inference and conversion (numeric, datetime)
- Command-line tool design with `argparse`
- Writing reusable, well-logged data pipelines
