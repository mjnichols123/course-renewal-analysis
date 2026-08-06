"""Functions for cleaning and validating the dataset tables."""

import pandas as pd


def clean_email_blasts(df: pd.DataFrame) -> pd.DataFrame:
    """Clean email blast records."""
    cleaned = df.copy()

    date_columns = [
        "sent_at",
        "blinded_course_2_exp",
        "blinded_course_9_exp",
        "blinded_course_10_exp",
    ]

    for column in date_columns:
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].replace("", pd.NA)
            cleaned[column] = pd.to_datetime(
                cleaned[column],
                errors="coerce",
            )

    if "is_large_blast" in cleaned.columns:
        cleaned["is_large_blast"] = pd.to_numeric(
            cleaned["is_large_blast"],
            errors="coerce",
        )

    return cleaned


def clean_expirations(df: pd.DataFrame) -> pd.DataFrame:
    """Clean expiration records."""
    cleaned = df.copy()

    if "expired_date" in cleaned.columns:
        cleaned["expired_date"] = cleaned["expired_date"].replace("", pd.NA)
        cleaned["expired_date"] = pd.to_datetime(
            cleaned["expired_date"],
            errors="coerce",
        )

    if "our_course" in cleaned.columns:
        cleaned["our_course"] = pd.to_numeric(
            cleaned["our_course"],
            errors="coerce",
        )

    return cleaned


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Clean order records."""
    cleaned = df.copy()

    if "created_at" in cleaned.columns:
        cleaned["created_at"] = cleaned["created_at"].replace("", pd.NA)
        cleaned["created_at"] = pd.to_datetime(
            cleaned["created_at"],
            errors="coerce",
        )

    if "price" in cleaned.columns:
        cleaned["price"] = cleaned["price"].replace("", pd.NA)
        cleaned["price"] = pd.to_numeric(
            cleaned["price"],
            errors="coerce",
        )

    return cleaned


def clean_tables(
    tables: dict[str, pd.DataFrame],
) -> dict[str, pd.DataFrame]:
    """Apply the correct cleaning function to each table."""
    cleaned_tables: dict[str, pd.DataFrame] = {}

    for name, df in tables.items():
        if name == "email_blasts.parquet":
            cleaned_tables[name] = clean_email_blasts(df)

        elif name == "expirations.parquet":
            cleaned_tables[name] = clean_expirations(df)

        elif name == "orders.parquet":
            cleaned_tables[name] = clean_orders(df)

        else:
            cleaned_tables[name] = df.copy()

    return cleaned_tables