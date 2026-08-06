import pandas as pd
from huggingface_hub import list_repo_files, hf_hub_download

DATASET_REPO = "fulldecent/mts_course_renewal_marketing"
DATA_DIR = "published_data"

def load_tables() -> dict[str, pd.DataFrame]:
    """Download and load all data files from the published_data directory."""
    all_files = list(
        list_repo_files(DATASET_REPO, repo_type="dataset")
    )
    data_files = [
        f for f in all_files
        if f.startswith(DATA_DIR + "/") and not f.endswith("/")
    ]

    tables: dict[str, pd.DataFrame] = {}
    for file_path in sorted(data_files):
        local_path = hf_hub_download(
            repo_id=DATASET_REPO,
            filename=file_path,
            repo_type="dataset",
        )
        name = file_path[len(DATA_DIR) + 1:]  # strip "published_data/"
        try:
            if file_path.endswith(".parquet"):
                tables[name] = pd.read_parquet(local_path)
            elif file_path.endswith(".csv"):
                tables[name] = pd.read_csv(local_path)
            elif file_path.endswith(".jsonl") or file_path.endswith(".json"):
                tables[name] = pd.read_json(local_path, lines=file_path.endswith(".jsonl"))
            else:
                print(f"Skipping unsupported file type: {file_path}")
        except Exception as exc:
            print(f"Error loading {file_path}: {exc}")

    return tables
