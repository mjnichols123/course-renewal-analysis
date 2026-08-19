"""Markdown report generation for exploratory findings."""

from pathlib import Path

import pandas as pd


REPORT_PATH = Path("reports/exploratory_findings.md")


def build_email_frequency_table(
    outcomes: pd.DataFrame,
) -> pd.DataFrame:
    """Create order-rate summary by pre-expiration email frequency."""

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
            observed=True,
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
        .reset_index()
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

    return summary


def build_email_timing_table(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
) -> pd.DataFrame:
    """Create order-rate summary by pre-expiration email timing."""

    keys = [
        "email_blinded_index",
        "expired_date",
        "course_blinded_index",
    ]

    pre_expiration = email_timing[
        email_timing["days_before_expiration"].between(
            0,
            180,
        )
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
        .reset_index()
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

    return summary


def write_exploratory_findings_report(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
) -> Path:
    """Write major exploratory email findings to Markdown."""

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    frequency = build_email_frequency_table(
        outcomes
    )

    timing = build_email_timing_table(
        outcomes,
        email_timing,
    )

    frequency_display = frequency.copy()

    frequency_display.columns = [
        "Pre-Expiration Emails",
        "Expiration Events",
        "30-Day Order Rate",
        "60-Day Order Rate",
        "90-Day Order Rate",
        "180-Day Order Rate",
    ]

    for column in [
        "30-Day Order Rate",
        "60-Day Order Rate",
        "90-Day Order Rate",
        "180-Day Order Rate",
    ]:
        frequency_display[column] = (
            frequency_display[column]
            .map(lambda value: f"{value:.2f}%")
        )

    timing_display = timing.copy()

    timing_display.columns = [
        "Email Timing",
        "Expiration Events",
        "Average Emails",
        "30-Day Order Rate",
        "60-Day Order Rate",
        "90-Day Order Rate",
        "180-Day Order Rate",
    ]

    timing_display["Average Emails"] = (
        timing_display["Average Emails"]
        .map(lambda value: f"{value:.2f}")
    )

    for column in [
        "30-Day Order Rate",
        "60-Day Order Rate",
        "90-Day Order Rate",
        "180-Day Order Rate",
    ]:
        timing_display[column] = (
            timing_display[column]
            .map(lambda value: f"{value:.2f}%")
        )

    content = f"""# Exploratory Analysis Findings

## Objective

This report summarizes major exploratory findings from the course renewal analysis. Results are generated directly from the project analysis pipeline so the tables can be reproduced by rerunning `analysis.py`.

The analysis examines associations between course expiration, email outreach, and subsequent customer ordering.

Because the orders table does not identify the specific course purchased, subsequent orders should not automatically be interpreted as confirmed course renewals.

## Pre-Expiration Email Frequency

The table below compares subsequent order rates based on the number of emails associated with an expiration event during the 180 days before expiration.

{frequency_display.to_markdown(index=False)}

### Interpretation

The most notable increase occurs between one and two pre-expiration emails.

Expiration events receiving zero or one email have similar 180-day subsequent order rates, while events receiving two or more emails show substantially higher observed order rates.

Additional emails beyond two show relatively little additional improvement in the aggregate results, suggesting a possible diminishing-return pattern.

These results are descriptive and should not be interpreted as evidence that sending additional emails causes the increase in ordering.

### Figure

![Order Rates by Email Frequency](figures/order_rates_by_email_frequency.png)

## Pre-Expiration Email Timing

The table below compares subsequent order rates based on when email outreach occurred before expiration.

{timing_display.to_markdown(index=False)}

### Interpretation

Outreach occurring within approximately 90 days before expiration is generally associated with stronger subsequent order rates than outreach occurring 91-180 days before expiration.

The 61-90 day group shows particularly strong short-term order rates, while the 31-60 day group has the highest observed 180-day order rate.

Timing groups are not mutually exclusive. An expiration event may appear in more than one timing group if emails were sent during multiple pre-expiration periods.

### Figure

![Order Rates by Email Timing](figures/order_rates_by_email_timing.png)

## Current Working Findings

The analysis currently suggests:

1. Pre-expiration outreach is associated with higher subsequent ordering than no pre-expiration outreach.
2. One email performs similarly to no email in the longer outcome windows.
3. The largest increase in observed order rates begins at two emails.
4. Additional emails beyond two show relatively limited incremental improvement.
5. Outreach occurring within roughly 90 days before expiration appears more strongly associated with subsequent ordering than outreach several months earlier.
6. These relationships are observational and should not be interpreted as causal without further analysis.

## Related Expiration-Window Analysis

A separate report examines order behavior within 30 days before and after expiration:

`reports/expiration_window_findings.md`

That analysis includes weekly order-distribution tables, CDF milestones, and PDF/CDF figures centered on expiration.

## Reproducibility

This report is generated programmatically from the current analysis outputs.

To regenerate it, run:

```bash
python3 analysis.py
```
"""