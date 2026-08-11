"""Visualizations for course renewal exploratory analysis."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


FIGURE_DIR = Path("reports/figures")


def plot_order_rates_by_email_frequency(
    outcomes: pd.DataFrame,
) -> Path:
    """Plot subsequent order rates by pre-expiration email frequency."""

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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
        )[
            [
                "order_within_30d",
                "order_within_60d",
                "order_within_90d",
                "order_within_180d",
            ]
        ]
        .mean()
        .mul(100)
    )

    summary.columns = [
        "30 days",
        "60 days",
        "90 days",
        "180 days",
    ]

    ax = summary.plot(
        kind="line",
        marker="o",
        figsize=(10, 6),
    )

    ax.set_title(
        "Subsequent Order Rates by Pre-Expiration Email Frequency"
    )

    ax.set_xlabel(
        "Number of Emails in 180 Days Before Expiration"
    )

    ax.set_ylabel(
        "Expiration Events Followed by an Order (%)"
    )

    ax.legend(
        title="Order Window"
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    output_path = (
        FIGURE_DIR
        / "order_rates_by_email_frequency.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_path