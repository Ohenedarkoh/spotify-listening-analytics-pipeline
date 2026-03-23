from pathlib import Path

import yaml
from google.cloud import storage


def load_config():
    # Central config keeps cloud targets consistent
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def upload_directory(local_dir: Path, bucket_name: str, prefix: str):
    # Mirrors local raw structure into GCS
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    for path in local_dir.rglob("*"):
        if path.is_file():
            rel_path = path.relative_to(local_dir).as_posix()
            blob_path = f"{prefix}/{rel_path}" if prefix else rel_path
            bucket.blob(blob_path).upload_from_filename(str(path))
            print(f"Uploaded: {path} -> gs://{bucket_name}/{blob_path}")


def main():
    config = load_config()
    bucket_name = config["gcp"]["gcs_bucket"]

    local_raw = Path(config["raw_output"]["base_path"])
    if not local_raw.exists():
        raise RuntimeError(f"Local raw path not found: {local_raw}")

    upload_directory(local_raw, bucket_name, prefix="raw")


if __name__ == "__main__":
    main()
