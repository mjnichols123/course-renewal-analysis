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

    print("\nOrder timing after email:")

    for start, end in [
        (0, 3),
        (4, 7),
        (8, 14),
        (15, 21),
        (22, 30),
    ]:
        count = email_order_timing[
            email_order_timing[
                "days_email_to_order"
            ].between(start, end)
        ].shape[0]

        rate = count / total * 100

        print(
            f"{start:>2}-{end:>2} days after email: "
            f"{count:>5,} ({rate:.2f}%)"
        )

    print("\nEmail timing before expiration:")

    for start, end in [
        (0, 7),
        (8, 14),
        (15, 21),
        (22, 30),
    ]:
        subset = email_order_timing[
            email_order_timing[
                "days_before_expiration"
            ].between(start, end)
        ]

        print(
            f"{start:>2}-{end:>2} days before expiration: "
            f"{len(subset):>5,}"
        )