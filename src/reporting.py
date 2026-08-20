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


def build_email_to_order_delay_table(
    email_order_timing: pd.DataFrame,
) -> pd.DataFrame:
    """Create distribution of delay from email to subsequent order."""

    total = len(email_order_timing)

    bins = [
        (0, 4),
        (4, 8),
        (8, 15),
        (15, 22),
        (22, 30.000001),
    ]

    labels = [
        "0-3 days",
        "4-7 days",
        "8-14 days",
        "15-21 days",
        "22-30 days",
    ]

    rows = []

    for (start, end), label in zip(
        bins,
        labels,
    ):
        count = (
            (
                email_order_timing["days_email_to_order"] >= start
            )
            & (
                email_order_timing["days_email_to_order"] < end
            )
        ).sum()

        rows.append(
            {
                "Delay After Email": label,
                "Email-Order Observations": count,
                "Percent of Observations": (
                    count / total * 100
                ),
            }
        )

    return pd.DataFrame(rows)


def build_first_email_final_week_table(
    email_timing: pd.DataFrame,
    orders: pd.DataFrame,
) -> pd.DataFrame:
    """Create final-week order-rate table by first email timing."""

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

    return summary





def write_exploratory_findings_report(
    outcomes: pd.DataFrame,
    email_timing: pd.DataFrame,
    email_order_timing: pd.DataFrame,
    orders: pd.DataFrame,
) -> Path:
    """Write major exploratory email findings to Markdown."""

    REPORT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ----------------------------------------------------------
    # BUILD ANALYSIS TABLES
    # ----------------------------------------------------------

    frequency = build_email_frequency_table(
        outcomes
    )

    timing = build_email_timing_table(
        outcomes,
        email_timing,
    )

    email_order_delay = build_email_to_order_delay_table(
        email_order_timing
    )

    first_email_final_week = build_first_email_final_week_table(
        email_timing,
        orders,
    )

    # ----------------------------------------------------------
    # FORMAT EMAIL FREQUENCY TABLE
    # ----------------------------------------------------------

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

    # ----------------------------------------------------------
    # FORMAT EMAIL TIMING TABLE
    # ----------------------------------------------------------

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

    # ----------------------------------------------------------
    # FORMAT EMAIL-TO-ORDER DELAY TABLE
    # ----------------------------------------------------------

    email_order_delay_display = (
        email_order_delay.copy()
    )

    email_order_delay_display[
        "Percent of Observations"
    ] = email_order_delay_display[
        "Percent of Observations"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    # ----------------------------------------------------------
    # FORMAT FIRST-EMAIL TIMING TABLE
    # ----------------------------------------------------------

    first_email_display = (
        first_email_final_week.copy()
    )

    first_email_display.columns = [
        "First Email Timing",
        "Expiration Events",
        "Final-Week Orders",
        "Final-Week Order Rate",
    ]

    first_email_display[
        "Final-Week Order Rate"
    ] = first_email_display[
        "Final-Week Order Rate"
    ].map(
        lambda value: f"{value:.2f}%"
    )

    # ----------------------------------------------------------
    # EMAIL-TO-ORDER SUMMARY STATISTICS
    # ----------------------------------------------------------

    median_email_to_order = (
        email_order_timing[
            "days_email_to_order"
        ].median()
    )

    mean_email_to_order = (
        email_order_timing[
            "days_email_to_order"
        ].mean()
    )

    # ----------------------------------------------------------
    # BUILD MARKDOWN REPORT
    # ----------------------------------------------------------

    content = f"""# Exploratory Analysis Findings

## Objective

This report summarizes major exploratory findings from the course renewal analysis. Results are generated directly from the project analysis pipeline so the tables can be reproduced by rerunning `analysis.py`.

The analysis examines associations between course expiration, email outreach, and subsequent customer ordering.

Because the orders table does not identify the specific course purchased, subsequent orders should not automatically be interpreted as confirmed course renewals.

---

## Pre-Expiration Email Frequency

The table below compares subsequent order rates based on the number of emails associated with an expiration event during the 180 days before expiration.

{frequency_display.to_markdown(index=False)}

### Interpretation

The most notable increase occurs between one and two pre-expiration emails.

Expiration events receiving zero or one email have similar longer-term subsequent order rates, while events receiving two or more emails show substantially higher observed order rates.

Additional emails beyond two show relatively little additional improvement in the aggregate results, suggesting a possible diminishing-return pattern.

These results are descriptive and should not be interpreted as evidence that sending additional emails causes the increase in ordering.

### Figure

![Order Rates by Email Frequency](figures/order_rates_by_email_frequency.png)

---

## Pre-Expiration Email Timing

The table below compares subsequent order rates based on when email outreach occurred before expiration.

{timing_display.to_markdown(index=False)}

### Interpretation

Outreach occurring within approximately 90 days before expiration is generally associated with stronger subsequent order rates than outreach occurring 91-180 days before expiration.

The 61-90 day group shows particularly strong short-term order rates, while the 31-60 day group has the highest observed 180-day order rate.

Timing groups in this analysis are not mutually exclusive. An expiration event may appear in more than one timing group if emails were sent during multiple pre-expiration periods.

### Figure

![Order Rates by Email Timing](figures/order_rates_by_email_timing.png)

---

## Email to Subsequent Order Timing

This analysis examines pre-expiration emails that were followed by a customer order within 30 days of the email.

Among these observations, the median delay from email to subsequent order was approximately **{median_email_to_order:.2f} days**, while the mean delay was approximately **{mean_email_to_order:.2f} days**.

{email_order_delay_display.to_markdown(index=False)}

### Interpretation

The largest share of matched email-to-order observations occurred 8-14 days after outreach.

Ordering was not concentrated exclusively in the first few days after an email. Instead, a substantial portion of subsequent orders occurred one to three weeks after outreach.

This provides useful context for the expiration-window findings because it suggests that customers may require time between receiving outreach and placing an order.

This analysis includes only emails that were followed by an order within 30 days. Therefore, the percentages above describe the timing distribution among matched email-to-order observations rather than the probability that an individual email produces an order.

---

## Final-Week Orders by First Email Timing

To create mutually exclusive timing groups, each expiration event was assigned according to its first observed email during the final 30 days before expiration.

The outcome measures whether a subsequent customer order occurred during the final seven days before expiration and after the email was sent.

{first_email_display.to_markdown(index=False)}

### Interpretation

A clear timing pattern appears in the final 30 days.

Expiration events whose first email occurred 22-30 days before expiration had the highest observed final-week subsequent-order rate.

The observed rates were:

- **22-30 days:** 5.49%
- **15-21 days:** 4.44%
- **8-14 days:** 2.45%
- **0-7 days:** 0.24%

The pattern suggests that beginning outreach before the final two weeks may provide customers more opportunity to act before expiration.

This finding is also consistent with the observed median email-to-order delay of approximately **{median_email_to_order:.2f} days**.

The result should not be interpreted as causal. Customers receiving earlier outreach may also receive additional emails later, meaning email timing and email frequency may interact. Customer characteristics, course characteristics, and other unobserved factors may also contribute to the differences.

---

## Current Working Findings

The exploratory analysis currently suggests:

1. **Pre-expiration outreach is associated with higher subsequent ordering.** Expiration events receiving outreach generally show higher subsequent order rates than events receiving no pre-expiration outreach.

2. **The largest frequency improvement occurs between one and two emails.** One email performs similarly to no email in several outcome windows, while two emails are associated with substantially higher observed order rates.

3. **Additional emails beyond two show diminishing aggregate improvement.** Three and four-or-more emails generally produce results similar to two emails rather than another large increase.

4. **Outreach within approximately 90 days of expiration appears more favorable than outreach much earlier.** The 91-180 day timing group generally shows weaker subsequent ordering.

5. **Order activity becomes particularly concentrated close to expiration.** The separate expiration-window analysis shows a substantial share of nearby orders occurring during the final week before expiration.

6. **Orders following outreach are often delayed rather than immediate.** Among matched email-to-order observations, the median delay is approximately **{median_email_to_order:.2f} days**.

7. **Within the final 30 days, earlier outreach is associated with stronger final-week ordering.** Using mutually exclusive first-email timing groups, the highest final-week subsequent-order rate occurs when outreach begins 22-30 days before expiration.

8. **The combined evidence suggests a possible 2-4 week outreach window.** Beginning outreach approximately 15-30 days before expiration may give customers sufficient time to respond while remaining close enough to expiration for the message to be relevant.

9. **These findings are observational rather than causal.** The available data cannot establish that email timing or frequency directly causes subsequent orders.

---

## Important Data Limitation

The orders table identifies the customer and order date but does not identify the specific course associated with the purchase.

As a result, this project measures **subsequent customer ordering around course expiration**, not confirmed renewal of the specific expiring course.

This distinction should be maintained when interpreting or presenting the results.

---

## Related Expiration-Window Analysis

A separate report examines customer order behavior within 30 days before and after expiration:

`reports/expiration_window_findings.md`

That analysis includes:

- weekly order-distribution tables,
- order concentration immediately before and after expiration,
- CDF milestones,
- PDF and CDF visualizations centered on expiration.

The expiration-window analysis complements the email analysis by showing when customer orders occur relative to the expiration date itself.

---

## Recommended Next Analysis

Future work should examine the interaction between **email frequency and email timing**.

In particular, the current analysis suggests that events whose first email occurs 15-30 days before expiration have stronger observed final-week order rates. However, those customers may also receive additional emails later.

A useful next step would therefore compare outcomes for combinations such as:

- first email 22-30 days before expiration with one total email,
- first email 22-30 days before expiration with two total emails,
- first email 15-21 days before expiration with one total email,
- first email 15-21 days before expiration with two or more emails.

This would help determine whether the observed timing pattern remains after accounting for outreach frequency.

---

## Reproducibility

This report is generated programmatically from the current analysis outputs.

To regenerate the analysis and this report, run:

```bash
python3 analysis.py
```
"""