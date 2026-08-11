"""Exploratory analysis functions for course renewal behavior."""

import pandas as pd


def prepare_expiration_order_pairs(
    expirations: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Match expiration records with subsequent customer orders.

    Each expiration is matched to orders belonging to the same customer.
    The number of days between expiration and order is calculated so that
    renewal/purchase behavior around expiration can be studied.

    This does not assume that an order is for the same course as the
    expiration because course information is not available in the orders
    table.
    """

    valid_expirations = expirations.dropna(
        subset=["expired_date"]
    ).copy()

    pairs = valid_expirations.merge(
        orders,
        on="email_blinded_index",
        how="inner",
    )

    pairs["days_from_expiration"] = (
        pairs["created_at"] - pairs["expired_date"]
    ).dt.total_seconds() / 86400

    return pairs


def summarize_order_timing(pairs: pd.DataFrame) -> None:
    """Print basic statistics about orders relative to expiration."""

    print("\n" + "=" * 70)
    print("ORDER TIMING RELATIVE TO EXPIRATION")
    print("=" * 70)

    print(f"Expiration-order pairs: {len(pairs):,}")

    print(
        "Customers represented:",
        f"{pairs['email_blinded_index'].nunique():,}",
    )

    print("\nDays from expiration summary:")
    print(
        pairs["days_from_expiration"].describe(
            percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
        )
    )

    windows = [30, 60, 90, 180]

    print("\nOrders after expiration:")

    for days in windows:
        count = (
            pairs["days_from_expiration"]
            .between(0, days)
            .sum()
        )

        print(f"Within {days:>3} days: {count:,}")

    print("\nOrders before expiration:")

    for days in windows:
        count = (
            pairs["days_from_expiration"]
            .between(-days, 0, inclusive="left")
            .sum()
        )

        print(f"Within {days:>3} days before: {count:,}")
        

def prepare_nearest_order_timing(
    expirations: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Find the nearest customer order before and after each expiration.

    Orders are matched at the customer level because the orders table does
    not identify which course was purchased.
    """

    valid_expirations = (
        expirations
        .dropna(subset=["expired_date"])
        .drop_duplicates()
        .copy()
    )

    valid_orders = (
        orders
        .drop_duplicates()
        .copy()
    )

    pairs = valid_expirations.merge(
        valid_orders,
        on="email_blinded_index",
        how="left",
    )

    pairs["days_from_expiration"] = (
        pairs["created_at"] - pairs["expired_date"]
    ).dt.total_seconds() / 86400

    before = (
        pairs[pairs["days_from_expiration"] < 0]
        .groupby(
            [
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
                "our_course",
            ]
        )["days_from_expiration"]
        .max()
        .rename("nearest_order_before_days")
    )

    after = (
        pairs[pairs["days_from_expiration"] >= 0]
        .groupby(
            [
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
                "our_course",
            ]
        )["days_from_expiration"]
        .min()
        .rename("nearest_order_after_days")
    )

    result = (
        valid_expirations
        .set_index(
            [
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
                "our_course",
            ]
        )
        .join(before)
        .join(after)
        .reset_index()
    )

    return result    


def summarize_nearest_order_timing(timing: pd.DataFrame) -> None:
    """Summarize nearest customer purchases around expiration."""

    print("\n" + "=" * 70)
    print("NEAREST ORDER TIMING AROUND EXPIRATION")
    print("=" * 70)

    print(f"Expiration events: {len(timing):,}")

    print(
        "Expiration events with a prior order:",
        f"{timing['nearest_order_before_days'].notna().sum():,}",
    )

    print(
        "Expiration events with a subsequent order:",
        f"{timing['nearest_order_after_days'].notna().sum():,}",
    )

    print("\nNearest order BEFORE expiration:")
    print(
        timing["nearest_order_before_days"].describe(
            percentiles=[0.25, 0.5, 0.75]
        )
    )

    print("\nNearest order AFTER expiration:")
    print(
        timing["nearest_order_after_days"].describe(
            percentiles=[0.25, 0.5, 0.75]
        )
    )

    print("\nExpiration events with an order within each window:")

    for days in [30, 60, 90, 180]:
        before = timing["nearest_order_before_days"].between(
            -days,
            0,
            inclusive="left",
        ).sum()

        after = timing["nearest_order_after_days"].between(
            0,
            days,
        ).sum()

        print(
            f"{days:>3} days | "
            f"before: {before:>6,} | "
            f"after: {after:>6,}"
        ) 
        
def prepare_email_expiration_timing(
    email_blasts: pd.DataFrame,
) -> pd.DataFrame:
    """Convert course expiration columns into a long-format email timing table."""

    course_columns = {
        "blinded_course_2_exp": 2,
        "blinded_course_9_exp": 9,
        "blinded_course_10_exp": 10,
    }

    records = []

    for column, course_id in course_columns.items():
        subset = email_blasts[
            [
                "email_blinded_index",
                "sent_at",
                "is_large_blast",
                column,
            ]
        ].dropna(subset=[column]).copy()

        subset = subset.rename(
            columns={column: "expired_date"}
        )

        subset["course_blinded_index"] = course_id

        subset["days_before_expiration"] = (
            subset["expired_date"] - subset["sent_at"]
        ).dt.total_seconds() / 86400

        records.append(subset)

    return pd.concat(
        records,
        ignore_index=True,
    )
    
def summarize_email_expiration_timing(
    email_timing: pd.DataFrame,
) -> None:
    """Summarize how email outreach is timed relative to expiration."""

    print("\n" + "=" * 70)
    print("EMAIL TIMING RELATIVE TO EXPIRATION")
    print("=" * 70)

    print(f"Email-expiration records: {len(email_timing):,}")

    print(
        "Customers represented:",
        f"{email_timing['email_blinded_index'].nunique():,}",
    )

    print("\nDays before expiration summary:")
    print(
        email_timing["days_before_expiration"].describe(
            percentiles=[0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]
        )
    )

    print("\nEmails sent before expiration:")

    for days in [30, 60, 90, 180]:
        count = email_timing[
            "days_before_expiration"
        ].between(
            0,
            days,
        ).sum()

        print(
            f"Within {days:>3} days before expiration: {count:,}"
        )

    print("\nEmails sent after expiration:")

    for days in [30, 60, 90, 180]:
        count = email_timing[
            "days_before_expiration"
        ].between(
            -days,
            0,
            inclusive="left",
        ).sum()

        print(
            f"Within {days:>3} days after expiration: {count:,}"
        )

    print("\nLarge vs non-large blast records:")
    print(
        email_timing["is_large_blast"]
        .value_counts()
        .sort_index()
    )