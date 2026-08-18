# Course Renewal Exploratory Analysis

## Objective

The purpose of this exploratory analysis is to examine the relationship between course expiration dates, email outreach, and subsequent customer orders. The broader goal is to identify patterns that may help improve the timing and frequency of renewal marketing.

Because the orders dataset identifies the customer and order date but does not identify the specific course purchased, subsequent orders should not automatically be interpreted as confirmed course renewals. The analysis therefore uses subsequent ordering behavior as an outcome associated with expiration and outreach events.

## Dataset Overview

The analysis uses three primary tables:

* **Email blasts:** 619,186 records covering 100,000 unique customer identifiers.
* **Expirations:** 127,928 expiration records covering 76,875 unique customers.
* **Orders:** 38,524 order records covering 18,537 unique customers.

There are 16,299 customers appearing in both the expiration and order datasets, providing a substantial overlapping population for studying purchasing behavior around expiration dates.

Initial data-quality analysis also identified duplicate records in the expiration and order tables, missing expiration dates, zero-dollar orders, and several unusually old or future expiration dates. These issues should be considered when interpreting results.

## Expiration and Order Timing

Initial matching of expiration events to customer orders showed that many orders occur far away from expiration dates. Because pairing every customer expiration with every customer order creates many unrelated combinations, the analysis was refined to identify the nearest order before and after each expiration event.

Among 122,705 distinct expiration events:

* 43,347 had a prior customer order.
* 17,375 had a subsequent customer order.
* 3,324 had a subsequent order within 30 days.
* 4,508 had a subsequent order within 60 days.
* 5,262 had a subsequent order within 90 days.
* 6,516 had a subsequent order within 180 days.

The large distance between many expiration events and their nearest orders indicates that not every expiration is closely associated with subsequent purchasing activity.

## Email Timing Around Expiration

The raw email-expiration matching produced 650,842 observations. Many represented expiration dates far removed from the email date, so the analysis was restricted to emails occurring within 180 days before or after expiration.

The resulting relevant outreach window contains:

* 102,128 email-expiration observations.
* 13,092 unique customers.
* 28,637 email records before expiration.
* 73,491 email records after expiration.

Most observations were non-large blasts, with 85,479 non-large blast records compared with 16,649 large blast records.

The relevant email data contains expiration information for blinded courses 2, 9, and 10.

## Pre-Expiration Outreach and Subsequent Orders

A dataset was constructed at the expiration-event level to compare expiration events that received email outreach during the previous 180 days with those that did not.

A total of 119,293 expiration events were analyzed:

* 9,601 received pre-expiration email outreach.
* 109,692 did not receive pre-expiration email outreach.

Expiration events receiving pre-expiration outreach were associated with higher subsequent order rates across every analyzed window.

| Subsequent Order Window | No Pre-Expiration Email | Received Pre-Expiration Email |
| ----------------------- | ----------------------: | ----------------------------: |
| 30 days                 |                   2.61% |                         4.71% |
| 60 days                 |                   3.51% |                         6.68% |
| 90 days                 |                   4.10% |                         7.70% |
| 180 days                |                   5.16% |                         8.48% |

These differences show a clear association between pre-expiration outreach and subsequent ordering behavior. They should not yet be interpreted as evidence that email outreach caused the increase because customers receiving outreach may differ systematically from customers who did not receive outreach.

## Email Frequency

The strongest pattern identified so far appears when pre-expiration outreach is separated by the number of emails associated with an expiration event.

| Pre-Expiration Emails | Expiration Events | 30-Day Order Rate | 60-Day Order Rate | 90-Day Order Rate | 180-Day Order Rate |
| --------------------- | ----------------: | ----------------: | ----------------: | ----------------: | -----------------: |
| 0                     |           109,692 |             2.61% |             3.51% |             4.10% |              5.16% |
| 1                     |             2,689 |             1.82% |             3.61% |             4.50% |              5.17% |
| 2                     |             1,439 |             5.56% |             7.71% |             8.83% |              9.80% |
| 3                     |             1,876 |             5.81% |             7.68% |             8.74% |              9.70% |
| 4+                    |             3,597 |             5.95% |             8.03% |             9.09% |              9.79% |

One pre-expiration email is associated with approximately the same 180-day order rate as no email at all. A substantial increase appears beginning at two emails.

Expiration events receiving two or more emails have 180-day order rates of approximately 9.7–9.8%, compared with approximately 5.2% for zero or one email.

There is little additional improvement in the observed order rate between two, three, and four or more emails. This suggests a possible threshold or diminishing-return pattern in which repeated outreach is associated with better outcomes, but additional contacts beyond the second email may provide limited incremental benefit.

This result is exploratory and does not establish that sending two emails causes higher order rates. Differences in customer selection, course type, expiration timing, or other characteristics may explain part of the relationship.

## Initial Findings

The exploratory analysis currently suggests:

1. Customer purchasing activity does cluster around some expiration events, although many expirations are not followed closely by an order.
2. Pre-expiration email outreach is associated with higher subsequent order rates.
3. A single email does not appear to be associated with a meaningful improvement compared with no outreach.
4. The largest observed improvement occurs when an expiration event receives at least two pre-expiration emails.
5. Increasing outreach beyond two emails has not produced a meaningful additional increase in observed order rates so far.
6. These findings represent associations and should not yet be interpreted as causal effects of email marketing.

## Next Analysis

The next stage will examine **email timing before expiration**.

Pre-expiration outreach will be separated into timing windows such as:

* 0–30 days before expiration
* 31–60 days before expiration
* 61–90 days before expiration
* 91–180 days before expiration

Subsequent order rates will then be compared across these timing windows.

Additional analysis should examine:

* Large versus non-large email blasts.
* Differences between blinded courses 2, 9, and 10.
* Differences between `our_course = 1` and `our_course = 0`.
* Interactions between email timing and email frequency.
* Whether the apparent improvement associated with two or more emails remains after controlling for other observable differences.

The eventual goal is to identify whether the data supports a practical renewal outreach strategy based on **when customers should be contacted and how many times they should be contacted before expiration**.

## Email Timing Before Expiration

Pre-expiration email outreach was divided into four timing windows to examine whether subsequent order behavior varies depending on when customers are contacted.

| Email Timing Before Expiration | Expiration Events | Average Emails | 30-Day Order Rate | 60-Day Order Rate | 90-Day Order Rate | 180-Day Order Rate |
| ------------------------------ | ----------------: | -------------: | ----------------: | ----------------: | ----------------: | -----------------: |
| 0–30 days                      |             8,833 |           2.29 |             4.78% |             6.81% |             7.85% |              8.68% |
| 31–60 days                     |             1,789 |           1.31 |             4.82% |             6.95% |             8.40% |              9.19% |
| 61–90 days                     |             1,367 |           1.28 |             5.49% |             7.69% |             8.42% |              9.08% |
| 91–180 days                    |             3,320 |           1.31 |             5.02% |             6.23% |             7.01% |              7.28% |

Outreach occurring 61–90 days before expiration is associated with the highest 30-day and 60-day subsequent order rates and a similarly strong 90-day rate. Outreach occurring 31–60 days before expiration has the highest observed 180-day order rate.

The 91–180 day window generally has lower longer-term order rates than outreach occurring within 90 days of expiration. This provides preliminary evidence that outreach closer to expiration may be more relevant than outreach occurring several months in advance.

However, timing cannot yet be evaluated independently from email frequency. Expiration events in the 0–30 day group received an average of 2.29 emails, compared with approximately 1.3 emails in the other timing groups. In addition, the same expiration event may appear in multiple timing groups when outreach occurred during multiple periods.

The current results therefore suggest that outreach within approximately 90 days of expiration may be particularly important, but additional analysis is needed to separate the effects of timing, frequency, and overlapping outreach strategies.


## Email Frequency and Timing Interaction

To better understand the relationship between email frequency and timing, expiration events receiving at least two pre-expiration emails were analyzed separately. A total of 6,922 expiration events received two or more emails within 180 days before expiration.

### Number of Timing Windows Reached

| Timing Windows Reached | Expiration Events | Average Emails | 30-Day Order Rate | 60-Day Order Rate | 90-Day Order Rate | 180-Day Order Rate |
| ---------------------- | ----------------: | -------------: | ----------------: | ----------------: | ----------------: | -----------------: |
| 1                      |             2,735 |           3.12 |             6.62% |             9.37% |            10.57% |             11.75% |
| 2                      |             2,956 |           3.48 |             5.33% |             6.61% |             7.56% |              8.24% |
| 3                      |               957 |           5.25 |             5.75% |             8.25% |             9.40% |              9.93% |
| 4                      |               274 |           7.75 |             3.65% |             5.11% |             5.84% |              5.84% |

The results do not show a consistent improvement from spreading outreach across a greater number of timing windows. Expiration events receiving repeated outreach within only one timing window had the highest observed subsequent order rates, including an 11.75% 180-day order rate.

Events receiving outreach across all four timing windows had the lowest observed rate. However, this group contains only 274 expiration events and received an average of 7.75 emails, so the result should be interpreted cautiously.

These findings do not support the initial hypothesis that distributing emails across more stages of the pre-expiration period necessarily produces better outcomes.

### Timing Among Events Receiving Two or More Emails

Among expiration events receiving at least two emails, order rates were also compared based on whether outreach occurred within each pre-expiration timing window.

| Outreach Window | Expiration Events | 30-Day Order Rate | 60-Day Order Rate | 90-Day Order Rate | 180-Day Order Rate |
| --------------- | ----------------: | ----------------: | ----------------: | ----------------: | -----------------: |
| 0–30 days       |             6,616 |             5.90% |             8.04% |             9.11% |              9.96% |
| 31–60 days      |             1,717 |             4.79% |             6.83% |             8.29% |              9.05% |
| 61–90 days      |             1,296 |             5.33% |             7.57% |             8.26% |              8.96% |
| 91–180 days     |             2,985 |             5.34% |             6.48% |             7.32% |              7.62% |

Within the repeated-outreach population, events receiving an email during the final 30 days before expiration have the highest observed 60-, 90-, and 180-day subsequent order rates. Outreach occurring 91–180 days before expiration is associated with the lowest 180-day rate.

Taken together with the email-frequency analysis, these results suggest that repeated outreach may be more important than simply distributing outreach across a large number of timing windows. Repeated outreach occurring closer to expiration may also be particularly relevant.

However, these timing groups overlap. An expiration event may receive emails in multiple windows and therefore appear in more than one timing-specific comparison. These findings should be treated as exploratory associations rather than estimates of causal marketing effects.


## Weekly Outreach Timing Within the Final 30 Days

Because the broader timing analysis suggested that outreach near expiration may be particularly important, the final 30 days before expiration were divided into approximately weekly intervals.

A total of 20,226 email-expiration observations occurred within the final 30 days, representing 8,823 expiration events.

| Timing Before Expiration | Expiration Events | Average Emails | 30-Day Order Rate | 60-Day Order Rate | 90-Day Order Rate | 180-Day Order Rate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0–7 days | 5,466 | 1.04 | 4.70% | 6.37% | 7.49% | 8.25% |
| 8–14 days | 4,544 | 1.01 | 5.44% | 7.84% | 8.92% | 9.69% |
| 15–21 days | 4,283 | 1.05 | 6.29% | 8.53% | 9.61% | 10.47% |
| 22–30 days | 4,904 | 1.12 | 6.19% | 8.68% | 9.78% | 10.74% |

The results show a notable pattern within the final month before expiration. Outreach occurring approximately two to four weeks before expiration is associated with stronger subsequent ordering than outreach occurring during the final week.

The 22–30 day group has the highest observed 60-, 90-, and 180-day order rates, including a 10.74% 180-day rate. The 15–21 day group has the highest 30-day rate at 6.29% and performs similarly strongly across the longer outcome windows.

In comparison, outreach during the final seven days before expiration has the lowest observed subsequent order rate across every outcome window, including an 8.25% 180-day rate.

Average email counts are relatively similar across the four timing groups, ranging from 1.01 to 1.12 emails per expiration event within each weekly window. This suggests that the observed timing differences are not obviously explained by substantially different email frequencies within the individual windows.

These results provide preliminary evidence of a possible pre-expiration outreach window approximately 15–30 days before expiration. However, expiration events may appear in multiple weekly timing groups if they received outreach during more than one part of the final month. The results therefore remain descriptive and should not be interpreted as causal effects of email timing.

## Expiration Window Analysis

To examine purchasing behavior immediately surrounding course expiration, orders were analyzed within a ±30-day window around each expiration event. For expiration events with at least one order in this window, the nearest order to expiration was selected.

### Key Findings

- 10,452 expiration events had an order within 30 days before or after expiration.
- 69.14% of nearby orders occurred before expiration, compared with 30.86% on or after expiration.
- The median order occurred approximately 4.83 days before expiration.
- The average order occurred approximately 4.97 days before expiration.
- Purchasing activity becomes increasingly concentrated as the expiration date approaches.
- The largest concentration of orders occurs immediately before expiration, with the PDF showing a pronounced peak near day 0.
- The CDF reaches approximately 69% by expiration, demonstrating that more than two-thirds of nearby purchasing activity occurs before the course expires.

### Interpretation

The results suggest that expiration acts as a meaningful purchasing deadline. Order activity increases as customers approach expiration and is most concentrated during the final days before expiration. After expiration, order activity drops substantially and gradually declines across the following 30 days.

This pattern should be considered alongside the email timing analysis. Earlier results showed stronger subsequent order rates among expiration events receiving outreach approximately 15–30 days before expiration than among those receiving outreach during the final week. Together, these findings suggest a possible pattern in which earlier outreach creates awareness or prompts consideration, while the actual purchase decision occurs closer to expiration. Additional analysis is needed before interpreting this relationship as causal.

### Order Concentration Around Expiration

Order activity within the ±30-day expiration window is strongly concentrated around the expiration date, particularly immediately before expiration.

Among 10,452 expiration events with an order within 30 days before or after expiration, 69.14% of the nearest orders occurred before expiration and 30.86% occurred on or after expiration.

The final seven days before expiration represented the single largest weekly concentration of ordering activity, accounting for 24.69% of all nearby orders. The cumulative distribution increased from 44.45% seven days before expiration to 69.14% by expiration.

Ordering activity declined substantially after expiration. By seven days after expiration, 82.65% of all orders in the ±30-day window had already occurred. By 14 days after expiration, 89.53% had occurred.

The median nearest order occurred approximately 4.83 days before expiration, further demonstrating that purchasing activity is centered shortly before the expiration date.

These findings suggest that expiration acts as a meaningful purchasing deadline. Customers who place orders near an expiration event are substantially more likely to do so before expiration, with the strongest concentration occurring during the final week.