"""Course renewal analysis.

Loads tables from the published_data directory of the
fulldecent/mts_course_renewal_marketing HuggingFace dataset and reports
basic statistics.
"""

"""Run the initial data-quality analysis for the course-renewal dataset."""

"""Main entry point for the Course Renewal Analysis project."""

from src.data_cleaning import clean_tables
from src.data_loading import load_tables
from src.data_profile import generate_data_profile
from src.data_summary import summarize_table
from src.exploratory_analysis import (
    prepare_expiration_order_pairs,
    summarize_order_timing,
    prepare_nearest_order_timing,
    summarize_nearest_order_timing,
    prepare_email_expiration_timing,
    summarize_email_expiration_timing,
    filter_relevant_email_timing,
    summarize_relevant_email_timing,
    build_expiration_outcome_dataset,
    summarize_outreach_outcomes,
    summarize_orders_by_email_frequency,
    summarize_orders_by_email_timing,
    summarize_frequency_timing_interaction,
    summarize_final_30_day_timing,
)

from src.visualizations import (
    plot_order_rates_by_email_frequency,
    plot_order_rates_by_email_timing,
    plot_order_rates_by_timing_windows,
    plot_order_cdf_around_expiration,
    plot_order_pdf_around_expiration,
)

from src.expiration_window_analysis import (
    create_expiration_window_tables,
    prepare_nearest_order_around_expiration,
    summarize_orders_around_expiration,
    write_expiration_window_report,
)

def main() -> None:
    """Load, clean, summarize, profile, and explore the dataset tables."""

    print("Loading tables...")
    raw_tables = load_tables()

    if not raw_tables:
        print("No tables found.")
        return

    print(f"Loaded {len(raw_tables)} tables.")

    print("Cleaning tables...")
    cleaned_tables = clean_tables(raw_tables)

    # Assign tables to shorter variable names
    expirations = cleaned_tables["expirations.parquet"]
    orders = cleaned_tables["orders.parquet"]
    nearest_30_day_orders = (
        prepare_nearest_order_around_expiration(
            expirations,
            orders,
            window_days=30,
        )
    )

    summarize_orders_around_expiration(
        nearest_30_day_orders,
    )
    
    distribution_table, cdf_table = (
        create_expiration_window_tables(
            nearest_30_day_orders,
        )
    )

    expiration_report_path = (
        write_expiration_window_report(
            nearest_30_day_orders,
            distribution_table,
            cdf_table,
            )
    )


    print(
        f"Expiration window report saved to: "
        f"{expiration_report_path}"
    )

    cdf_path = plot_order_cdf_around_expiration(
        nearest_30_day_orders,
    )

    pdf_path = plot_order_pdf_around_expiration(
        nearest_30_day_orders,
    )

    print(
        f"\nOrder CDF figure saved to: {cdf_path}"
    )

    print(
        f"Order PDF figure saved to: {pdf_path}"
    )
    
    email_blasts = cleaned_tables["email_blasts.parquet"]

    # Order timing analysis
    expiration_order_pairs = prepare_expiration_order_pairs(
        expirations,
        orders,
    )

    summarize_order_timing(
        expiration_order_pairs
    )

    nearest_order_timing = prepare_nearest_order_timing(
        expirations,
        orders,
    )

    summarize_nearest_order_timing(
        nearest_order_timing
    )


    # Email timing analysis
    email_timing = prepare_email_expiration_timing(
        email_blasts,
    )

    summarize_email_expiration_timing(
        email_timing,
    )
    
    relevant_email_timing = filter_relevant_email_timing(
    email_timing,
    window_days=180,
    )

    summarize_relevant_email_timing(
        relevant_email_timing,
    )
    
    outcomes = build_expiration_outcome_dataset(
    expirations,
    relevant_email_timing,
    orders,
    )

    summarize_outreach_outcomes(
        outcomes,
    )
    
    summarize_orders_by_email_frequency(
        outcomes,
    )
    
    summarize_orders_by_email_timing(
        outcomes,
        relevant_email_timing,
    )
    
    summarize_frequency_timing_interaction(
        outcomes,
        relevant_email_timing,
    )
    
    summarize_final_30_day_timing(
        outcomes,
        relevant_email_timing,
    )
    
    frequency_figure_path = plot_order_rates_by_email_frequency(
        outcomes,
    )

    print(
        f"\nEmail frequency figure saved to: "
        f"{frequency_figure_path}"
    )

    timing_figure_path = plot_order_rates_by_email_timing(
        outcomes,
        relevant_email_timing,
    )

    print(
        f"Email timing figure saved to: "
        f"{timing_figure_path}"
    )

    timing_windows_figure_path = plot_order_rates_by_timing_windows(
        outcomes,
        relevant_email_timing,
    )

    print(
        f"Timing windows figure saved to: "
        f"{timing_windows_figure_path}"
    )
    
    # Terminal data summaries
    print("\nGenerating terminal summaries...")

    for name, df in cleaned_tables.items():
        summarize_table(name, df)


    # Additional dataset checks
    print("\nCourse expiration breakdown:")
    print(
        expirations
        .groupby(["course_blinded_index", "our_course"])
        .size()
        .unstack(fill_value=0)
    )

    print("\nUnique customers by our_course:")
    print(
        expirations
        .groupby("our_course")["email_blinded_index"]
        .nunique()
    )

    print("\nOrder customer overlap:")

    expiration_customers = set(
        expirations["email_blinded_index"]
    )

    order_customers = set(
        orders["email_blinded_index"]
    )

    print(
        "Expiration customers:",
        len(expiration_customers),
    )

    print(
        "Order customers:",
        len(order_customers),
    )

    print(
        "Customers appearing in both:",
        len(expiration_customers & order_customers),
    )


    # Generate Markdown profile
    print("\nGenerating Markdown data profile...")

    report_path = generate_data_profile(
        cleaned_tables
    )

    print(
        f"Data profile saved to: {report_path}"
    )


if __name__ == "__main__":
    main()