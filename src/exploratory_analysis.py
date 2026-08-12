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
    
def filter_relevant_email_timing(
    email_timing: pd.DataFrame,
    window_days: int = 180,
) -> pd.DataFrame:
    """Keep email-expiration records within the analysis window."""

    relevant = email_timing[
        email_timing["days_before_expiration"].between(
            -window_days,
            window_days,
        )
    ].copy()

    return relevant


def summarize_relevant_email_timing(
    email_timing: pd.DataFrame,
) -> None:
    """Summarize email activity near course expiration."""

    print("\n" + "=" * 70)
    print("RELEVANT EMAIL OUTREACH WINDOW")
    print("=" * 70)

    print(
        "Email-expiration records:",
        f"{len(email_timing):,}",
    )

    print(
        "Customers represented:",
        f"{email_timing['email_blinded_index'].nunique():,}",
    )

    before = email_timing[
        email_timing["days_before_expiration"] >= 0
    ]

    after = email_timing[
        email_timing["days_before_expiration"] < 0
    ]

    print(
        "Emails before expiration:",
        f"{len(before):,}",
    )

    print(
        "Emails after expiration:",
        f"{len(after):,}",
    )

    print("\nBy blast type:")
    print(
        email_timing["is_large_blast"]
        .value_counts()
        .sort_index()
    )

    print("\nBy course:")
    print(
        email_timing["course_blinded_index"]
        .value_counts()
        .sort_index()
    )
    
def build_expiration_outcome_dataset(
    expirations: pd.DataFrame,
    email_timing: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Build one row per expiration event with outreach and order outcomes."""

    expiration_events = (
        expirations
        .dropna(subset=["expired_date"])
        .drop_duplicates()
        .copy()
    )

    # Restrict to courses represented in the email-blast dataset.
    expiration_events = expiration_events[
        expiration_events["course_blinded_index"].isin([2, 9, 10])
    ].copy()

    # ---------------------------------------------------------
    # Pre-expiration email exposure
    # ---------------------------------------------------------

    pre_expiration_emails = email_timing[
        email_timing["days_before_expiration"].between(
            0,
            180,
        )
    ].copy()

    email_summary = (
        pre_expiration_emails
        .groupby(
            [
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
            ]
        )
        .agg(
            pre_expiration_emails=(
                "sent_at",
                "count",
            ),
            large_blast_emails=(
                "is_large_blast",
                "sum",
            ),
        )
        .reset_index()
    )

    email_summary["non_large_blast_emails"] = (
        email_summary["pre_expiration_emails"]
        - email_summary["large_blast_emails"]
    )

    expiration_events = expiration_events.merge(
        email_summary,
        on=[
            "email_blinded_index",
            "expired_date",
            "course_blinded_index",
        ],
        how="left",
    )

    email_columns = [
        "pre_expiration_emails",
        "large_blast_emails",
        "non_large_blast_emails",
    ]

    expiration_events[email_columns] = (
        expiration_events[email_columns]
        .fillna(0)
        .astype(int)
    )

    expiration_events["received_pre_expiration_email"] = (
        expiration_events["pre_expiration_emails"] > 0
    ).astype(int)

    # ---------------------------------------------------------
    # Subsequent order outcomes
    # ---------------------------------------------------------

    order_pairs = expiration_events[
        [
            "email_blinded_index",
            "expired_date",
            "course_blinded_index",
        ]
    ].merge(
        orders[
            [
                "email_blinded_index",
                "created_at",
            ]
        ].drop_duplicates(),
        on="email_blinded_index",
        how="left",
    )

    order_pairs["days_after_expiration"] = (
        order_pairs["created_at"]
        - order_pairs["expired_date"]
    ).dt.total_seconds() / 86400

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    for days in [30, 60, 90, 180]:

        qualifying = (
            order_pairs[
                order_pairs["days_after_expiration"].between(
                    0,
                    days,
                )
            ]
            .groupby(keys)
            .size()
            .gt(0)
            .astype(int)
            .rename(f"order_within_{days}d")
            .reset_index()
        )

        expiration_events = expiration_events.merge(
            qualifying,
            on=keys,
            how="left",
        )

        expiration_events[f"order_within_{days}d"] = (
            expiration_events[f"order_within_{days}d"]
            .fillna(0)
            .astype(int)
        )

    return expiration_events

def summarize_outreach_outcomes(
    outcomes: pd.DataFrame,
) -> None:
    """Compare subsequent order rates by pre-expiration outreach."""

    print("\n" + "=" * 70)
    print("PRE-EXPIRATION OUTREACH VS SUBSEQUENT ORDERS")
    print("=" * 70)

    print(f"Expiration events analyzed: {len(outcomes):,}")

    print(
        "Events receiving pre-expiration outreach:",
        f"{outcomes['received_pre_expiration_email'].sum():,}",
    )

    print(
        "Events receiving no pre-expiration outreach:",
        f"{(outcomes['received_pre_expiration_email'] == 0).sum():,}",
    )

    print("\nSubsequent order rates:")

    for days in [30, 60, 90, 180]:

        column = f"order_within_{days}d"

        rates = (
            outcomes
            .groupby("received_pre_expiration_email")[column]
            .mean()
            .mul(100)
        )

        no_email_rate = rates.get(0, float("nan"))
        email_rate = rates.get(1, float("nan"))

        print(f"\nWithin {days} days:")
        print(
            f"  No pre-expiration email: {no_email_rate:.2f}%"
        )
        print(
            f"  Received pre-expiration email: {email_rate:.2f}%"
        )
        
def summarize_orders_by_email_frequency(
    outcomes: pd.DataFrame,
) -> None:
    """Compare subsequent order rates by number of pre-expiration emails."""

    print("\n" + "=" * 70)
    print("ORDER RATES BY PRE-EXPIRATION EMAIL FREQUENCY")
    print("=" * 70)

    analysis = outcomes.copy()

    analysis["email_frequency_group"] = pd.cut(
        analysis["pre_expiration_emails"],
        bins=[-1, 0, 1, 2, 3, float("inf")],
        labels=[
            "0 emails",
            "1 email",
            "2 emails",
            "3 emails",
            "4+ emails",
        ],
    )

    summary = (
        analysis
        .groupby(
            "email_frequency_group",
            observed=False,
        )
        .agg(
            expiration_events=(
                "email_blinded_index",
                "size",
            ),
            order_rate_30d=(
                "order_within_30d",
                "mean",
            ),
            order_rate_60d=(
                "order_within_60d",
                "mean",
            ),
            order_rate_90d=(
                "order_within_90d",
                "mean",
            ),
            order_rate_180d=(
                "order_within_180d",
                "mean",
            ),
        )
    )

    rate_columns = [
        "order_rate_30d",
        "order_rate_60d",
        "order_rate_90d",
        "order_rate_180d",
    ]

    summary[rate_columns] = (
        summary[rate_columns] * 100
    )

    print(summary.round(2).to_string())
    
    
def summarize_orders_by_email_timing(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
) -> None:
    """Compare subsequent order rates by timing of pre-expiration outreach."""

    print("\n" + "=" * 70)
    print("ORDER RATES BY PRE-EXPIRATION EMAIL TIMING")
    print("=" * 70)

    pre_expiration = email_timing[
        email_timing["days_before_expiration"].between(0, 180)
    ].copy()

    # Assign each email to a timing bucket.
    pre_expiration["timing_group"] = pd.cut(
        pre_expiration["days_before_expiration"],
        bins=[-0.001, 30, 60, 90, 180],
        labels=[
            "0-30 days",
            "31-60 days",
            "61-90 days",
            "91-180 days",
        ],
        include_lowest=True,
    )

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    # One row per expiration event and timing bucket.
    timing_exposure = (
        pre_expiration
        .dropna(subset=["timing_group"])
        .groupby(
            keys + ["timing_group"],
            observed=True,
        )
        .size()
        .rename("emails_in_timing_group")
        .reset_index()
    )

    timing_exposure = timing_exposure[
        timing_exposure["emails_in_timing_group"] > 0
    ]

    # Add order outcomes.
    timing_outcomes = timing_exposure.merge(
        outcomes[
            keys
            + [
                "order_within_30d",
                "order_within_60d",
                "order_within_90d",
                "order_within_180d",
            ]
        ],
        on=keys,
        how="left",
    )

    summary = (
        timing_outcomes
        .groupby(
            "timing_group",
            observed=True,
        )
        .agg(
            expiration_events=(
                "email_blinded_index",
                "size",
            ),
            average_emails=(
                "emails_in_timing_group",
                "mean",
            ),
            order_rate_30d=(
                "order_within_30d",
                "mean",
            ),
            order_rate_60d=(
                "order_within_60d",
                "mean",
            ),
            order_rate_90d=(
                "order_within_90d",
                "mean",
            ),
            order_rate_180d=(
                "order_within_180d",
                "mean",
            ),
        )
    )

    rate_columns = [
        "order_rate_30d",
        "order_rate_60d",
        "order_rate_90d",
        "order_rate_180d",
    ]

    summary[rate_columns] = (
        summary[rate_columns] * 100
    )

    print(summary.round(2).to_string())
    
def summarize_frequency_timing_interaction(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
) -> None:
    """Analyze order rates for repeated outreach across timing windows."""

    print("\n" + "=" * 70)
    print("EMAIL FREQUENCY + TIMING INTERACTION")
    print("=" * 70)

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    pre_expiration = email_timing[
        email_timing["days_before_expiration"].between(0, 180)
    ].copy()

    # Create indicators showing whether an expiration event
    # received at least one email in each timing window.
    pre_expiration["email_0_30"] = (
        pre_expiration["days_before_expiration"]
        .between(0, 30)
        .astype(int)
    )

    pre_expiration["email_31_60"] = (
        pre_expiration["days_before_expiration"]
        .between(30, 60, inclusive="right")
        .astype(int)
    )

    pre_expiration["email_61_90"] = (
        pre_expiration["days_before_expiration"]
        .between(60, 90, inclusive="right")
        .astype(int)
    )

    pre_expiration["email_91_180"] = (
        pre_expiration["days_before_expiration"]
        .between(90, 180, inclusive="right")
        .astype(int)
    )

    exposure = (
        pre_expiration
        .groupby(keys)
        .agg(
            total_emails=("sent_at", "count"),
            email_0_30=("email_0_30", "max"),
            email_31_60=("email_31_60", "max"),
            email_61_90=("email_61_90", "max"),
            email_91_180=("email_91_180", "max"),
        )
        .reset_index()
    )

    # Focus on expiration events receiving repeated outreach.
    exposure = exposure[
        exposure["total_emails"] >= 2
    ].copy()

    timing_columns = [
        "email_0_30",
        "email_31_60",
        "email_61_90",
        "email_91_180",
    ]

    exposure["timing_windows_reached"] = (
        exposure[timing_columns].sum(axis=1)
    )

    interaction = exposure.merge(
        outcomes[
            keys
            + [
                "order_within_30d",
                "order_within_60d",
                "order_within_90d",
                "order_within_180d",
            ]
        ],
        on=keys,
        how="left",
    )

    print(
        "Expiration events with 2+ emails:",
        f"{len(interaction):,}",
    )

    print("\nOrder rates by number of timing windows reached:")

    summary = (
        interaction
        .groupby("timing_windows_reached")
        .agg(
            expiration_events=(
                "email_blinded_index",
                "size",
            ),
            average_emails=(
                "total_emails",
                "mean",
            ),
            order_rate_30d=(
                "order_within_30d",
                "mean",
            ),
            order_rate_60d=(
                "order_within_60d",
                "mean",
            ),
            order_rate_90d=(
                "order_within_90d",
                "mean",
            ),
            order_rate_180d=(
                "order_within_180d",
                "mean",
            ),
        )
    )

    rate_columns = [
        "order_rate_30d",
        "order_rate_60d",
        "order_rate_90d",
        "order_rate_180d",
    ]

    summary[rate_columns] = (
        summary[rate_columns] * 100
    )

    print(summary.round(2).to_string())

    print("\n2+ email events by timing window:")

    for column, label in [
        ("email_0_30", "0-30 days"),
        ("email_31_60", "31-60 days"),
        ("email_61_90", "61-90 days"),
        ("email_91_180", "91-180 days"),
    ]:

        subset = interaction[
            interaction[column] == 1
        ]

        if len(subset) == 0:
            continue

        print(f"\n{label}:")
        print(f"  Expiration events: {len(subset):,}")

        for days in [30, 60, 90, 180]:
            rate = (
                subset[f"order_within_{days}d"].mean()
                * 100
            )

            print(
                f"  {days}-day order rate: {rate:.2f}%"
            )