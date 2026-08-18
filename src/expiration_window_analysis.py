"""Analysis of customer behavior around course expiration dates."""

import pandas as pd


def prepare_nearest_order_around_expiration(
    expirations: pd.DataFrame,
    orders: pd.DataFrame,
    window_days: int = 30,
) -> pd.DataFrame:
    """Find the nearest order within +/- window_days of each expiration."""

    expiration_events = (
        expirations
        .dropna(subset=["expired_date"])
        .drop_duplicates(
            subset=[
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
            ]
        )
        .copy()
    )

    order_data = (
        orders[
            [
                "email_blinded_index",
                "created_at",
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    pairs = expiration_events.merge(
        order_data,
        on="email_blinded_index",
        how="inner",
    )

    pairs["days_from_expiration"] = (
        pairs["created_at"] - pairs["expired_date"]
    ).dt.total_seconds() / 86400

    pairs = pairs[
        pairs["days_from_expiration"].between(
            -window_days,
            window_days,
        )
    ].copy()

    pairs["absolute_days_from_expiration"] = (
        pairs["days_from_expiration"].abs()
    )

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    nearest = (
        pairs
        .sort_values("absolute_days_from_expiration")
        .drop_duplicates(
            subset=keys,
            keep="first",
        )
        .copy()
    )

    return nearest


def summarize_orders_around_expiration(
    nearest_orders: pd.DataFrame,
) -> None:
    """Summarize nearest orders within 30 days of expiration."""

    print("\n" + "=" * 70)
    print("ORDER DISTRIBUTION WITHIN +/- 30 DAYS OF EXPIRATION")
    print("=" * 70)

    total = len(nearest_orders)

    if total == 0:
        print("No nearby orders found.")
        return

    days = nearest_orders["days_from_expiration"]

    before = nearest_orders[
        days < 0
    ]

    after = nearest_orders[
        days >= 0
    ]

    print(
        f"Expiration events with nearby order: {total:,}"
    )

    print(
        f"Orders before expiration: {len(before):,} "
        f"({len(before) / total * 100:.2f}%)"
    )

    print(
        f"Orders on/after expiration: {len(after):,} "
        f"({len(after) / total * 100:.2f}%)"
    )

    print("\nDistribution around expiration:")

    bins = [
        (-30, -21),
        (-21, -14),
        (-14, -7),
        (-7, 0),
        (0, 7),
        (7, 14),
        (14, 21),
        (21, 30.000001),
    ]

    labels = [
        "-30 to -22 days",
        "-21 to -15 days",
        "-14 to -8 days",
        "-7 to -1 days",
        "0 to 6 days",
        "7 to 13 days",
        "14 to 20 days",
        "21 to 30 days",
    ]

    for (start, end), label in zip(bins, labels):

        count = (
            (days >= start)
            & (days < end)
        ).sum()

        rate = count / total * 100

        print(
            f"{label:>15}: "
            f"{count:>5,} ({rate:.2f}%)"
        )

    print("\nCDF milestones:")

    milestones = [
        -21,
        -14,
        -7,
        0,
        7,
        14,
        21,
        30,
    ]

    for milestone in milestones:

        cumulative_count = (
            days <= milestone
        ).sum()

        cumulative_rate = (
            cumulative_count / total * 100
        )

        print(
            f"By day {milestone:>3}: "
            f"{cumulative_count:>5,} "
            f"({cumulative_rate:.2f}%)"
        )

    print("\nDays from expiration summary:")

    print(
        days.describe(
            percentiles=[
                0.10,
                0.25,
                0.50,
                0.75,
                0.90,
            ]
        )
    )