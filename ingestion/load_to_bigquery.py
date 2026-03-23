import json
from pathlib import Path

import yaml
from google.cloud import bigquery


def load_config():
    # Single source of truth for project + dataset
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_recently_played_json(local_dir: Path):
    # Collect listening events from raw JSON files
    records = []
    for file in local_dir.rglob("recently_played_*.json"):
        with file.open("r", encoding="utf-8") as f:
            payload = json.load(f)
            records.extend(payload.get("items", []))
    return records


def main():
    config = load_config()
    project_id = config["gcp"]["project_id"]
    dataset = config["gcp"]["bq_dataset"]

    client = bigquery.Client(project=project_id)
    table_id = f"{project_id}.{dataset}.listening_history_raw"

    local_raw = Path(config["raw_output"]["base_path"])
    rows = load_recently_played_json(local_raw)

    if not rows:
        print("No rows found to load.")
        return

        # Raw layer: append-only, allow schema growth
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition="WRITE_APPEND",
        autodetect=True,
        schema_update_options=[bigquery.SchemaUpdateOption.ALLOW_FIELD_ADDITION],
    )

    load_job = client.load_table_from_json(rows, table_id, job_config=job_config)
    load_job.result()

    print(f"Loaded {len(rows)} rows into {table_id}")



if __name__ == "__main__":
    main()
