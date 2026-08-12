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

def plot_order_rates_by_email_timing(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
) -> Path:
    """Plot 180-day order rates by pre-expiration email timing."""

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    pre_expiration = email_timing[
        email_timing["days_before_expiration"].between(0, 180)
    ].copy()

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

    timing_exposure = (
        pre_expiration
        .dropna(subset=["timing_group"])
        .groupby(
            keys + ["timing_group"],
            observed=True,
        )
        .size()
        .rename("email_count")
        .reset_index()
    )

    timing_outcomes = timing_exposure.merge(
        outcomes[
            keys
            + [
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
        )["order_within_180d"]
        .mean()
        .mul(100)
    )

    ax = summary.plot(
        kind="bar",
        figsize=(9, 6),
    )

    ax.set_title(
        "180-Day Order Rate by Pre-Expiration Email Timing"
    )

    ax.set_xlabel(
        "Email Timing Before Expiration"
    )

    ax.set_ylabel(
        "Expiration Events Followed by an Order (%)"
    )

    ax.tick_params(
        axis="x",
        rotation=0,
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    output_path = (
        FIGURE_DIR
        / "order_rates_by_email_timing.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_path

def plot_order_rates_by_timing_windows(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
) -> Path:
    """Plot 180-day order rates by number of timing windows reached."""

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    pre_expiration = email_timing[
        email_timing["days_before_expiration"].between(0, 180)
    ].copy()

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

    # Focus on repeated outreach.
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
        exposure[timing_columns]
        .sum(axis=1)
    )

    interaction = exposure.merge(
        outcomes[
            keys
            + [
                "order_within_180d",
            ]
        ],
        on=keys,
        how="left",
    )

    summary = (
        interaction
        .groupby("timing_windows_reached")[
            "order_within_180d"
        ]
        .mean()
        .mul(100)
    )

    summary.index = [
        f"{int(value)} window"
        if int(value) == 1
        else f"{int(value)} windows"
        for value in summary.index
    ]

    ax = summary.plot(
        kind="bar",
        figsize=(9, 6),
    )

    ax.set_title(
        "180-Day Order Rate by Number of Timing Windows Reached"
    )

    ax.set_xlabel(
        "Timing Windows Reached by 2+ Emails"
    )

    ax.set_ylabel(
        "Expiration Events Followed by an Order (%)"
    )

    ax.tick_params(
        axis="x",
        rotation=0,
    )

    ax.grid(
        axis="y",
        alpha=0.3,
    )

    plt.tight_layout()

    output_path = (
        FIGURE_DIR
        / "order_rates_by_timing_windows.png"
    )

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    return output_path