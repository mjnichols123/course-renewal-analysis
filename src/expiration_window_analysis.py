"""Analysis of customer behavior around course expiration dates."""

import pandas as pd
from pathlib import Path

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


def create_expiration_window_tables(
    nearest_orders: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create weekly distribution and CDF milestone tables."""

    days = nearest_orders["days_from_expiration"]
    total = len(nearest_orders)

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
        "30-22 days before",
        "21-15 days before",
        "14-8 days before",
        "7-1 days before",
        "0-6 days after",
        "7-13 days after",
        "14-20 days after",
        "21-30 days after",
    ]

    distribution_rows = []

    for (start, end), label in zip(bins, labels):
        count = (
            (days >= start)
            & (days < end)
        ).sum()

        distribution_rows.append(
            {
                "Timing Relative to Expiration": label,
                "Expiration Events": count,
                "Percent of Nearby Orders": (
                    count / total * 100
                ),
            }
        )

    distribution_table = pd.DataFrame(
        distribution_rows
    )

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

    milestone_labels = [
        "21 days before",
        "14 days before",
        "7 days before",
        "Expiration",
        "7 days after",
        "14 days after",
        "21 days after",
        "30 days after",
    ]

    cdf_rows = []

    for milestone, label in zip(
        milestones,
        milestone_labels,
    ):
        count = (
            days <= milestone
        ).sum()

        cdf_rows.append(
            {
                "Milestone": label,
                "Cumulative Orders": count,
                "Cumulative Percentage": (
                    count / total * 100
                ),
            }
        )

    cdf_table = pd.DataFrame(cdf_rows)

    return distribution_table, cdf_table


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
    
    
def write_expiration_window_report(
    nearest_orders: pd.DataFrame,
    distribution_table: pd.DataFrame,
    cdf_table: pd.DataFrame,
) -> Path:
    """Write expiration-window findings to a Markdown report."""

    report_path = Path(
        "reports/expiration_window_findings.md"
    )

    report_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    days = nearest_orders["days_from_expiration"]

    total = len(nearest_orders)
    before = (days < 0).sum()
    after = (days >= 0).sum()

    median_day = days.median()
    mean_day = days.mean()

    distribution_display = (
        distribution_table.copy()
    )

    distribution_display[
        "Percent of Nearby Orders"
    ] = distribution_display[
        "Percent of Nearby Orders"
    ].map(lambda value: f"{value:.2f}%")

    cdf_display = cdf_table.copy()

    cdf_display[
        "Cumulative Percentage"
    ] = cdf_display[
        "Cumulative Percentage"
    ].map(lambda value: f"{value:.2f}%")

    content = f"""# Expiration Window Analysis

## Overview

This analysis examines customer ordering behavior within 30 days before and after course expiration.

For each expiration event, the nearest order occurring within the ±30-day window was selected. A total of **{total:,} expiration events** had a nearby order.

## Before vs. After Expiration

- Orders before expiration: **{before:,} ({before / total * 100:.2f}%)**
- Orders on or after expiration: **{after:,} ({after / total * 100:.2f}%)**
- Mean order timing: **{mean_day:.2f} days relative to expiration**
- Median order timing: **{median_day:.2f} days relative to expiration**

## Weekly Distribution

{distribution_display.to_markdown(index=False)}

## Cumulative Distribution Milestones

{cdf_display.to_markdown(index=False)}

## Key Findings

Order activity within the ±30-day expiration window is strongly concentrated around the expiration date.

The largest weekly concentration of nearby orders occurs during the final seven days before expiration. Overall, more than two-thirds of nearby orders occur before expiration.

The cumulative distribution also shows that most nearby purchasing activity occurs by shortly after expiration. This indicates that the period immediately surrounding expiration represents an especially important part of the customer purchasing lifecycle.

## Figures

### Order Distribution Around Expiration

![Order Distribution Around Expiration](figures/order_pdf_around_expiration.png)

### Cumulative Distribution of Orders

![Cumulative Distribution of Orders](figures/order_cdf_around_expiration.png)

## Interpretation Note

These percentages describe the distribution of orders among expiration events that had an order within the ±30-day window. They should not be interpreted as the overall probability that an expiration event results in an order.
"""

    report_path.write_text(
        content,
        encoding="utf-8",
    )

    return report_path