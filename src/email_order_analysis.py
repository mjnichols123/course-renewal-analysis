"""Analysis connecting pre-expiration email outreach to subsequent orders."""

import pandas as pd

def prepare_email_to_order_timing(
    email_timing: pd.DataFrame,
    orders: pd.DataFrame,
    max_email_days_before: int = 30,
    max_order_delay_days: int = 30,
) -> pd.DataFrame:
    """Connect pre-expiration emails to the next subsequent customer order."""

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    emails = email_timing[
        email_timing["days_before_expiration"].between(
            0,
            max_email_days_before,
        )
    ].copy()

    emails = (
        emails[
            keys
            + [
                "sent_at",
                "days_before_expiration",
                "is_large_blast",
            ]
        ]
        .drop_duplicates()
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

    pairs = emails.merge(
        order_data,
        on="email_blinded_index",
        how="left",
    )

    pairs["days_email_to_order"] = (
        pairs["created_at"] - pairs["sent_at"]
    ).dt.total_seconds() / 86400

    pairs["days_order_from_expiration"] = (
        pairs["created_at"] - pairs["expired_date"]
    ).dt.total_seconds() / 86400

    subsequent = pairs[
        pairs["days_email_to_order"].between(
            0,
            max_order_delay_days,
        )
    ].copy()

    subsequent = (
        subsequent
        .sort_values("days_email_to_order")
        .drop_duplicates(
            subset=keys + ["sent_at"],
            keep="first",
        )
    )

    return subsequent


def summarize_email_to_order_timing(
    email_order_timing: pd.DataFrame,
) -> None:
    """Summarize timing from pre-expiration email to subsequent order."""

    print("\n" + "=" * 70)
    print("EMAIL TO SUBSEQUENT ORDER TIMING")
    print("=" * 70)

    total = len(email_order_timing)

    if total == 0:
        print("No email-to-order observations found.")
        return

    print(
        f"Emails followed by an order within 30 days: "
        f"{total:,}"
    )

    print("\nDays from email to subsequent order:")

    print(
        email_order_timing[
            "days_email_to_order"
        ].describe(
            percentiles=[
                0.10,
                0.25,
                0.50,
                0.75,
                0.90,
            ]
        )
    )

    # ----------------------------------------------------------
    # DISTRIBUTION OF TIME FROM EMAIL TO SUBSEQUENT ORDER
    # ----------------------------------------------------------

    print("\nOrder timing after email:")

    timing_bins = [
        (0, 4),
        (4, 8),
        (8, 15),
        (15, 22),
        (22, 30.000001),
    ]

    timing_labels = [
        "0-3 days",
        "4-7 days",
        "8-14 days",
        "15-21 days",
        "22-30 days",
    ]

    for (start, end), label in zip(
        timing_bins,
        timing_labels,
    ):
        count = (
            (
                email_order_timing[
                    "days_email_to_order"
                ] >= start
            )
            & (
                email_order_timing[
                    "days_email_to_order"
                ] < end
            )
        ).sum()

        rate = count / total * 100

        print(
            f"{label:>10} after email: "
            f"{count:>5,} ({rate:.2f}%)"
        )

    # ----------------------------------------------------------
    # TIMING OF THE EMAIL RELATIVE TO EXPIRATION
    # ----------------------------------------------------------

    print("\nEmail timing before expiration:")

    email_bins = [
        (0, 8),
        (8, 15),
        (15, 22),
        (22, 30.000001),
    ]

    email_labels = [
        "0-7 days",
        "8-14 days",
        "15-21 days",
        "22-30 days",
    ]

    for (start, end), label in zip(
        email_bins,
        email_labels,
    ):
        count = (
            (
                email_order_timing[
                    "days_before_expiration"
                ] >= start
            )
            & (
                email_order_timing[
                    "days_before_expiration"
                ] < end
            )
        ).sum()

        rate = count / total * 100

        print(
            f"{label:>10} before expiration: "
            f"{count:>5,} ({rate:.2f}%)"
        )
        
        
def summarize_order_rates_by_email_week(
    email_timing: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    """Compare subsequent order rates by email timing within final 30 days."""

    print("\n" + "=" * 70)
    print("ORDER RATES BY EMAIL WEEK WITHIN FINAL 30 DAYS")
    print("=" * 70)

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    emails = email_timing[
        email_timing["days_before_expiration"].between(
            0,
            30,
        )
    ].copy()

    bins = [
        (0, 8),
        (8, 15),
        (15, 22),
        (22, 30.000001),
    ]

    labels = [
        "0-7 days",
        "8-14 days",
        "15-21 days",
        "22-30 days",
    ]

    email_rows = []

    for (start, end), label in zip(
        bins,
        labels,
    ):
        subset = emails[
            (emails["days_before_expiration"] >= start)
            & (emails["days_before_expiration"] < end)
        ]

        events = (
            subset[keys]
            .drop_duplicates()
            .copy()
        )

        events["email_timing_group"] = label

        email_rows.append(events)

    email_events = pd.concat(
        email_rows,
        ignore_index=True,
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

    pairs = email_events.merge(
        order_data,
        on="email_blinded_index",
        how="left",
    )

    pairs["days_order_from_expiration"] = (
        pairs["created_at"]
        - pairs["expired_date"]
    ).dt.total_seconds() / 86400

    # Subsequent order within 30 days after expiration event.
    pairs["order_within_30d_after_expiration"] = (
        pairs["days_order_from_expiration"].between(
            0,
            30,
        )
    ).astype(int)

    # Order occurs before expiration but after the email window began.
    pairs["order_before_expiration"] = (
        (pairs["days_order_from_expiration"] < 0)
        & (pairs["days_order_from_expiration"] >= -30)
    ).astype(int)

    event_summary = (
        pairs
        .groupby(
            keys + ["email_timing_group"],
            observed=True,
        )
        .agg(
            order_before_expiration=(
                "order_before_expiration",
                "max",
            ),
            order_within_30d_after_expiration=(
                "order_within_30d_after_expiration",
                "max",
            ),
        )
        .reset_index()
    )

    summary = (
        event_summary
        .groupby(
            "email_timing_group",
            observed=True,
        )
        .agg(
            expiration_events=(
                "email_blinded_index",
                "size",
            ),
            before_expiration_order_rate=(
                "order_before_expiration",
                "mean",
            ),
            post_expiration_30d_order_rate=(
                "order_within_30d_after_expiration",
                "mean",
            ),
        )
    )

    summary[
        [
            "before_expiration_order_rate",
            "post_expiration_30d_order_rate",
        ]
    ] *= 100

    print(summary.round(2).to_string())
    
    
def summarize_final_week_orders_by_email_week(
    email_timing: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    """Compare final-week order rates by timing of earlier email outreach."""

    print("\n" + "=" * 70)
    print("FINAL-WEEK ORDER RATE BY EMAIL TIMING")
    print("=" * 70)

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    emails = email_timing[
        email_timing["days_before_expiration"].between(
            0,
            30,
        )
    ].copy()

    bins = [
        (0, 8),
        (8, 15),
        (15, 22),
        (22, 30.000001),
    ]

    labels = [
        "0-7 days",
        "8-14 days",
        "15-21 days",
        "22-30 days",
    ]

    results = []

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

    for (start, end), label in zip(
        bins,
        labels,
    ):
        window_emails = emails[
            (emails["days_before_expiration"] >= start)
            & (emails["days_before_expiration"] < end)
        ].copy()

        # Use the first email observed in this timing window
        # for each expiration event.
        event_emails = (
            window_emails
            .sort_values("sent_at")
            .drop_duplicates(
                subset=keys,
                keep="first",
            )
        )

        pairs = event_emails[
            keys + ["sent_at"]
        ].merge(
            order_data,
            on="email_blinded_index",
            how="left",
        )

        pairs["days_order_from_expiration"] = (
            pairs["created_at"]
            - pairs["expired_date"]
        ).dt.total_seconds() / 86400

        # Must occur AFTER the email.
        pairs["after_email"] = (
            pairs["created_at"] >= pairs["sent_at"]
        )

        # Our specific business outcome:
        # an order in the final seven days before expiration.
        pairs["final_week_order"] = (
            pairs["after_email"]
            & (
                pairs["days_order_from_expiration"]
                >= -7
            )
            & (
                pairs["days_order_from_expiration"]
                < 0
            )
        )

        event_results = (
            pairs
            .groupby(keys)
            .agg(
                final_week_order=(
                    "final_week_order",
                    "max",
                )
            )
            .reset_index()
        )

        event_count = len(event_results)
        order_count = (
            event_results["final_week_order"].sum()
        )

        order_rate = (
            order_count / event_count * 100
            if event_count
            else 0
        )

        results.append(
            {
                "email_timing": label,
                "expiration_events": event_count,
                "final_week_orders": order_count,
                "final_week_order_rate": order_rate,
            }
        )

    summary = pd.DataFrame(results)

    print(
        summary
        .round(2)
        .to_string(index=False)
    )
    
    
def summarize_final_week_orders_by_first_email(
    email_timing: pd.DataFrame,
    orders: pd.DataFrame,
) -> None:
    """Compare final-week order rates using first email in final 30 days."""

    print("\n" + "=" * 70)
    print("FINAL-WEEK ORDER RATE BY FIRST EMAIL TIMING")
    print("=" * 70)

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    emails = email_timing[
        email_timing["days_before_expiration"].between(
            0,
            30,
        )
    ].copy()

    # The earliest email chronologically is the email furthest
    # from expiration, making groups mutually exclusive.
    first_emails = (
        emails
        .sort_values("sent_at")
        .drop_duplicates(
            subset=keys,
            keep="first",
        )
        .copy()
    )

    first_emails["first_email_timing"] = pd.cut(
        first_emails["days_before_expiration"],
        bins=[
            -0.001,
            8,
            15,
            22,
            30.000001,
        ],
        labels=[
            "0-7 days",
            "8-14 days",
            "15-21 days",
            "22-30 days",
        ],
        right=False,
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

    pairs = first_emails[
        keys
        + [
            "sent_at",
            "first_email_timing",
        ]
    ].merge(
        order_data,
        on="email_blinded_index",
        how="left",
    )

    pairs["days_order_from_expiration"] = (
        pairs["created_at"]
        - pairs["expired_date"]
    ).dt.total_seconds() / 86400

    pairs["final_week_order"] = (
        (pairs["created_at"] >= pairs["sent_at"])
        & (pairs["days_order_from_expiration"] >= -7)
        & (pairs["days_order_from_expiration"] < 0)
    )

    event_results = (
        pairs
        .groupby(
            keys + ["first_email_timing"],
            observed=True,
        )
        .agg(
            final_week_order=(
                "final_week_order",
                "max",
            )
        )
        .reset_index()
    )

    summary = (
        event_results
        .groupby(
            "first_email_timing",
            observed=True,
        )
        .agg(
            expiration_events=(
                "email_blinded_index",
                "size",
            ),
            final_week_orders=(
                "final_week_order",
                "sum",
            ),
            final_week_order_rate=(
                "final_week_order",
                "mean",
            ),
        )
        .reset_index()
    )

    summary["final_week_order_rate"] *= 100

    print(
        summary
        .round(2)
        .to_string(index=False)
    )