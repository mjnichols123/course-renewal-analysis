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


def main() -> None:
    """Load, clean, summarize, and profile the dataset tables."""
    print("Loading tables...")
    raw_tables = load_tables()

    if not raw_tables:
        print("No tables found.")
        return

    print(f"Loaded {len(raw_tables)} tables.")

    print("Cleaning tables...")
    cleaned_tables = clean_tables(raw_tables)

    print("Generating terminal summaries...")

    for name, df in cleaned_tables.items():
        summarize_table(name, df)

    print("Generating Markdown data profile...")
    report_path = generate_data_profile(cleaned_tables)

    print(f"Data profile saved to: {report_path}")


if __name__ == "__main__":
    main()