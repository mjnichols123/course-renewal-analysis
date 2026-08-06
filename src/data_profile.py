"""Create detailed data profiles for the course-renewal dataset."""

from pathlib import Path
from typing import Any

import pandas as pd


REPORT_PATH = Path("reports/data_profile.md")


TABLE_DESCRIPTIONS = {
    "email_blasts.parquet": (
        "Each row represents one blinded email recipient included in an "
        "email blast sent on a particular date."
    ),
    "email_blasts.csv": (
        "Each row represents one blinded email recipient included in an "
        "email blast sent on a particular date."
    ),
    "expirations.parquet": (
        "Each row represents one certification-course expiration associated "
        "with a blinded email identifier."
    ),
    "expirations.csv": (
        "Each row represents one certification-course expiration associated "
        "with a blinded email identifier."
    ),
    "orders.parquet": (
        "Each row represents one order associated with a blinded email "
        "identifier."
    ),
    "orders.csv": (
        "Each row represents one order associated with a blinded email "
        "identifier."
    ),
}


def format_value(value: Any) -> str:
    """Format values safely for inclusion in a Markdown report."""
    if pd.isna(value):
        return "Missing"

    if isinstance(value, pd.Timestamp):
        return value.isoformat()

    return str(value).replace("|", "\\|")


def classify_column(column: pd.Series) -> str:
    """Assign a general analytical role to a column."""
    name = column.name.lower()

    if "index" in name or name.endswith("_id"):
        return "Identifier"

    if pd.api.types.is_datetime64_any_dtype(column):
        return "Date/time"

    if pd.api.types.is_bool_dtype(column):
        return "Boolean"

    if pd.api.types.is_numeric_dtype(column):
        unique_count = column.nunique(dropna=True)

        if unique_count <= 2:
            return "Binary indicator"

        return "Numeric"

    unique_count = column.nunique(dropna=True)

    if unique_count <= 50:
        return "Categorical"

    return "Text or high-cardinality categorical"


def find_candidate_keys(df: pd.DataFrame) -> list[str]:
    """Return columns whose nonmissing values uniquely identify rows."""
    candidates: list[str] = []

    for column in df.columns:
        series = df[column]

        if series.isna().any():
            continue

        if series.nunique(dropna=False) == len(df):
            candidates.append(column)

    return candidates


def find_candidate_composite_keys(
    name: str,
    df: pd.DataFrame,
) -> list[list[str]]:
    """Check sensible table-specific combinations for uniqueness."""
    possible_keys: dict[str, list[list[str]]] = {
        "email_blasts.parquet": [
            ["sent_at", "email_blinded_index"],
            ["sent_at", "email_blinded_index", "is_large_blast"],
        ],
        "email_blasts.csv": [
            ["sent_at", "email_blinded_index"],
            ["sent_at", "email_blinded_index", "is_large_blast"],
        ],
        "expirations.parquet": [
            [
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
                "our_course",
            ],
        ],
        "expirations.csv": [
            [
                "email_blinded_index",
                "expired_date",
                "course_blinded_index",
                "our_course",
            ],
        ],
        "orders.parquet": [
            ["created_at", "email_blinded_index", "price"],
        ],
        "orders.csv": [
            ["created_at", "email_blinded_index", "price"],
        ],
    }

    unique_combinations: list[list[str]] = []

    for columns in possible_keys.get(name, []):
        if not all(column in df.columns for column in columns):
            continue

        duplicate_count = df.duplicated(subset=columns).sum()

        if duplicate_count == 0:
            unique_combinations.append(columns)

    return unique_combinations


def get_top_values(
    series: pd.Series,
    limit: int = 5,
) -> pd.DataFrame:
    """Return the most common values and their percentages."""
    counts = series.value_counts(dropna=False).head(limit)

    result = counts.rename_axis("value").reset_index(name="count")
    result["percentage"] = result["count"] / len(series) * 100

    return result


def build_column_profile(df: pd.DataFrame) -> pd.DataFrame:
    """Build a column-level summary table."""
    records: list[dict[str, Any]] = []

    for column_name in df.columns:
        series = df[column_name]
        missing_count = int(series.isna().sum())
        unique_count = int(series.nunique(dropna=True))

        records.append(
            {
                "column": column_name,
                "dtype": str(series.dtype),
                "role": classify_column(series),
                "missing": missing_count,
                "missing_pct": missing_count / len(df) * 100,
                "unique": unique_count,
                "unique_pct": unique_count / len(df) * 100,
            }
        )

    return pd.DataFrame(records)


def append_markdown_table(
    lines: list[str],
    dataframe: pd.DataFrame,
) -> None:
    """Append a DataFrame as a basic Markdown table."""
    if dataframe.empty:
        lines.append("No results.")
        lines.append("")
        return

    headers = [str(column) for column in dataframe.columns]

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in dataframe.itertuples(index=False, name=None):
        formatted_row = [format_value(value) for value in row]
        lines.append("| " + " | ".join(formatted_row) + " |")

    lines.append("")


def profile_table(name: str, df: pd.DataFrame) -> list[str]:
    """Generate one table's Markdown profile."""
    lines: list[str] = []

    lines.append(f"## {name}")
    lines.append("")
    lines.append(TABLE_DESCRIPTIONS.get(name, "Description not yet defined."))
    lines.append("")

    duplicate_count = int(df.duplicated().sum())

    lines.append("### Table summary")
    lines.append("")
    lines.append(f"- Rows: {len(df):,}")
    lines.append(f"- Columns: {len(df.columns):,}")
    lines.append(f"- Fully duplicated rows: {duplicate_count:,}")
    lines.append(
        f"- Duplicate-row percentage: "
        f"{duplicate_count / len(df) * 100:.2f}%"
    )
    lines.append("")

    lines.append("### Column profile")
    lines.append("")

    column_profile = build_column_profile(df).copy()
    column_profile["missing_pct"] = column_profile["missing_pct"].map(
        lambda value: f"{value:.2f}%"
    )
    column_profile["unique_pct"] = column_profile["unique_pct"].map(
        lambda value: f"{value:.2f}%"
    )

    append_markdown_table(lines, column_profile)

    lines.append("### Candidate keys")
    lines.append("")

    single_keys = find_candidate_keys(df)
    composite_keys = find_candidate_composite_keys(name, df)

    if not single_keys and not composite_keys:
        lines.append(
            "No tested single-column or table-specific composite key "
            "uniquely identifies every row."
        )
        lines.append("")
    else:
        for column in single_keys:
            lines.append(f"- Single-column candidate: `{column}`")

        for columns in composite_keys:
            formatted_columns = ", ".join(
                f"`{column}`" for column in columns
            )
            lines.append(f"- Composite candidate: {formatted_columns}")

        lines.append("")

    lines.append("### Date ranges")
    lines.append("")

    datetime_columns = df.select_dtypes(
        include=["datetime", "datetimetz"]
    ).columns

    if len(datetime_columns) == 0:
        lines.append("No datetime columns were detected.")
        lines.append("")
    else:
        date_records: list[dict[str, Any]] = []

        for column in datetime_columns:
            date_records.append(
                {
                    "column": column,
                    "minimum": df[column].min(),
                    "maximum": df[column].max(),
                }
            )

        append_markdown_table(lines, pd.DataFrame(date_records))

    lines.append("### Most common values")
    lines.append("")

    for column in df.columns:
        series = df[column]

        if (
            pd.api.types.is_datetime64_any_dtype(series)
            or series.nunique(dropna=True) > 100
        ):
            continue

        lines.append(f"#### `{column}`")
        lines.append("")

        top_values = get_top_values(series).copy()
        top_values["percentage"] = top_values["percentage"].map(
            lambda value: f"{value:.2f}%"
        )

        append_markdown_table(lines, top_values)

    lines.append("### Initial business interpretation")
    lines.append("")

    if "email_blinded_index" in df.columns:
        customer_count = df["email_blinded_index"].nunique(dropna=True)
        records_per_customer = len(df) / customer_count

        lines.append(
            f"- Unique blinded email identifiers: {customer_count:,}"
        )
        lines.append(
            f"- Average records per blinded email identifier: "
            f"{records_per_customer:.2f}"
        )

    if name.startswith("email_blasts") and "sent_at" in df.columns:
        blast_dates = df["sent_at"].nunique(dropna=True)
        lines.append(f"- Unique email blast dates: {blast_dates:,}")

    if name.startswith("expirations") and "course_blinded_index" in df.columns:
        course_count = df["course_blinded_index"].nunique(dropna=True)
        lines.append(f"- Unique blinded courses: {course_count:,}")

    if name.startswith("orders") and "price" in df.columns:
        lines.append(f"- Total recorded revenue: ${df['price'].sum():,.2f}")
        lines.append(f"- Median order price: ${df['price'].median():,.2f}")

    lines.append("")
    return lines


def add_relationship_profile(
    lines: list[str],
    tables: dict[str, pd.DataFrame],
) -> None:
    """Describe overlap in identifiers between the dataset tables."""
    lines.append("## Relationships between tables")
    lines.append("")

    identifier_sets: dict[str, set[Any]] = {}

    for name, df in tables.items():
        if "email_blinded_index" in df.columns:
            identifier_sets[name] = set(
                df["email_blinded_index"].dropna().unique()
            )

    names = sorted(identifier_sets)

    if len(names) < 2:
        lines.append(
            "Not enough tables contain `email_blinded_index` to compare."
        )
        lines.append("")
        return

    relationship_records: list[dict[str, Any]] = []

    for left_position, left_name in enumerate(names):
        for right_name in names[left_position + 1:]:
            left_ids = identifier_sets[left_name]
            right_ids = identifier_sets[right_name]
            overlap = left_ids & right_ids

            relationship_records.append(
                {
                    "left_table": left_name,
                    "right_table": right_name,
                    "left_unique_ids": len(left_ids),
                    "right_unique_ids": len(right_ids),
                    "shared_ids": len(overlap),
                    "left_overlap_pct": (
                        len(overlap) / len(left_ids) * 100
                        if left_ids
                        else 0
                    ),
                    "right_overlap_pct": (
                        len(overlap) / len(right_ids) * 100
                        if right_ids
                        else 0
                    ),
                }
            )

    relationship_df = pd.DataFrame(relationship_records)
    relationship_df["left_overlap_pct"] = (
        relationship_df["left_overlap_pct"]
        .map(lambda value: f"{value:.2f}%")
    )
    relationship_df["right_overlap_pct"] = (
        relationship_df["right_overlap_pct"]
        .map(lambda value: f"{value:.2f}%")
    )

    append_markdown_table(lines, relationship_df)

    lines.append("### Working entity relationship model")
    lines.append("")
    lines.append("```text")
    lines.append("email_blinded_index")
    lines.append("        │")
    lines.append("        ├── email_blasts")
    lines.append("        ├── expirations")
    lines.append("        └── orders")
    lines.append("```")
    lines.append("")


def generate_data_profile(
    tables: dict[str, pd.DataFrame],
    output_path: Path = REPORT_PATH,
) -> Path:
    """Generate and save the full Markdown data-profile report."""
    lines: list[str] = [
        "# Course Renewal Dataset Profile",
        "",
        "This report was generated automatically from the cleaned tables.",
        "",
        "## Dataset overview",
        "",
    ]

    overview_records = [
        {
            "table": name,
            "rows": len(df),
            "columns": len(df.columns),
            "duplicate_rows": int(df.duplicated().sum()),
        }
        for name, df in tables.items()
    ]

    append_markdown_table(lines, pd.DataFrame(overview_records))
    add_relationship_profile(lines, tables)

    for name, df in tables.items():
        lines.extend(profile_table(name, df))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines), encoding="utf-8")

    return output_path