"""Functions for summarizing and validating cleaned dataset tables."""

import pandas as pd


def validate_table(name: str, df: pd.DataFrame) -> None:
    """Print table-specific data-quality checks."""
    print("\nValidation Checks:")
    print(f"Duplicate rows: {df.duplicated().sum():,}")

    if name == "email_blasts.parquet":
        if "is_large_blast" in df.columns:
            valid_values = [0, 1]

            unexpected_values = (
                df.loc[
                    df["is_large_blast"].notna()
                    & ~df["is_large_blast"].isin(valid_values),
                    "is_large_blast",
                ]
                .drop_duplicates()
                .tolist()
            )

            print(
                "Unexpected is_large_blast values: "
                f"{unexpected_values}"
            )

            print(
                "Large blast rows: "
                f"{(df['is_large_blast'] == 1).sum():,}"
            )

            print(
                "Non-large blast rows: "
                f"{(df['is_large_blast'] == 0).sum():,}"
            )

    elif name == "expirations.parquet":
        if "our_course" in df.columns:
            valid_values = [0, 1]

            unexpected_values = (
                df.loc[
                    df["our_course"].notna()
                    & ~df["our_course"].isin(valid_values),
                    "our_course",
                ]
                .drop_duplicates()
                .tolist()
            )

            print(
                "Unexpected our_course values: "
                f"{unexpected_values}"
            )

            print(
                "Our-course expiration rows: "
                f"{(df['our_course'] == 1).sum():,}"
            )

            print(
                "Other-course expiration rows: "
                f"{(df['our_course'] == 0).sum():,}"
            )

    elif name == "orders.parquet":
        if "price" in df.columns:
            print(
                "Missing prices: "
                f"{df['price'].isna().sum():,}"
            )

            print(
                "Zero-dollar orders: "
                f"{(df['price'] == 0).sum():,}"
            )

            print(
                "Negative-price orders: "
                f"{(df['price'] < 0).sum():,}"
            )


def print_date_ranges(df: pd.DataFrame) -> None:
    """Print the minimum and maximum values of datetime columns."""
    datetime_columns = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns

    print("\nDate Ranges:")

    if len(datetime_columns) == 0:
        print("No datetime columns.")
        return

    for column in datetime_columns:
        minimum_date = df[column].min()
        maximum_date = df[column].max()

        print(
            f"{column}: "
            f"{minimum_date} through {maximum_date}"
        )


def summarize_table(name: str, df: pd.DataFrame) -> None:
    """Print an exploratory and data-quality summary of one table."""
    print("\n" + "=" * 70)
    print(f"TABLE: {name}")
    print("=" * 70)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns):,}")

    print("\nColumn Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    missing_values = df.isna().sum()
    missing_values = missing_values[missing_values > 0]

    if missing_values.empty:
        print("No missing values.")
    else:
        print(missing_values)

    print("\nUnique Values Per Column:")
    print(df.nunique(dropna=True))

    print_date_ranges(df)

    print("\nFirst Five Rows:")
    print(df.head())

    validate_table(name, df)