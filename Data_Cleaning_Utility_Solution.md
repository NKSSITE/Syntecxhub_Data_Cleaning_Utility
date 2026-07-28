# Data Cleaning Utility

## Objective

Build a Python utility using Pandas to clean a dataset.

## Features

-   Detect missing values.
-   Handle missing values by dropping, filling, or imputing them.
-   Convert incorrect data types such as dates and numeric columns.
-   Parse date columns.
-   Remove duplicate records.
-   Standardise column names by trimming whitespace, converting to
    lowercase, and replacing spaces with underscores.
-   Save the cleaned dataset.
-   Produce a brief cleaning log summarising the performed operations.

## Typical Workflow

1.  Load the dataset with Pandas.
2.  Inspect missing values using `isnull()` or `isna()`.
3.  Clean missing values with `dropna()` or `fillna()`.
4.  Convert data types using `pd.to_numeric()` and `pd.to_datetime()`.
5.  Remove duplicate rows with `drop_duplicates()`.
6.  Standardise column names.
7.  Export the cleaned dataset to a new CSV file.
8.  Print or save a cleaning log.

## Output

-   `cleaned_data.csv`
-   A short cleaning log describing the changes made.
