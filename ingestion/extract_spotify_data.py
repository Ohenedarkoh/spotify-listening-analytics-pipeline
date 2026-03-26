import json
import os
from datetime import datetime, timezone
from pathlib import Path
import yaml

from dotenv import load_dotenv

from spotify_client import SpotifyClient


def ensure_dir(path: Path):
    # Create partition directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)


def write_json(payload, out_path: Path):
    # Persist raw payload exactly as received
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

def load_config():
    # Single source of truth for runtime settings
    with open("configs/config.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_watermark(path: Path) -> int:
    # Returns last processed play time in ms
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return int(data.get("last_played_at_ms", 0))


def save_watermark(path: Path, value_ms: int):
    # Writes the latest processed play time
    if not path.parent.exists():
        raise RuntimeError(f"State dir missing: {path.parent}")
    with path.open("w", encoding="utf-8") as f:
        json.dump({"last_played_at_ms": value_ms}, f, indent=2)


def played_at_to_ms(played_at: str) -> int:
    # Spotify timestamps are UTC ISO strings
    dt = datetime.fromisoformat(played_at.replace("Z", "+00:00"))
    return int(dt.timestamp() * 1000)



def main():
    # Load local secrets (do not commit configs/.env)
    load_dotenv("configs/.env")
    config = load_config()
    watermark_path = Path(config["incremental"]["watermark_path"])
    last_ms = load_watermark(watermark_path)


    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    if not all([client_id, client_secret, redirect_uri]):
        raise RuntimeError("Missing Spotify env vars. Check configs/.env")

    scopes = ["user-read-recently-played"]
    client = SpotifyClient(client_id, client_secret, redirect_uri, scopes)

    refresh_token = os.getenv("SPOTIFY_REFRESH_TOKEN")

    if refresh_token:
        token = client.refresh_access_token(refresh_token)
        access_token = token["access_token"]
    else:
        print("Open this URL in a browser and approve access:")
        print(client.auth_url())

        code = input("Paste the code from the redirect URL: ").strip()
        token = client.exchange_code_for_token(code)

        access_token = token["access_token"]
        refresh_token = token.get("refresh_token")
        if refresh_token:
            print("Save this refresh token securely for future runs:")
            print(refresh_token)


    # Pull a single batch for now (50 most recent)
        # Pull plays after last watermark (if any)
    payload = client.get_recently_played(
        access_token=access_token,
        limit=50,
        after_ms=last_ms if last_ms else None,
    )

    items = payload.get("items", [])
    if last_ms:
        items = [i for i in items if played_at_to_ms(i["played_at"]) > last_ms]

    # Deduplicate within this batch
    seen = set()
    deduped = []
    for item in items:
        key = (item.get("played_at"), item.get("track", {}).get("id"))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)

    if not deduped:
        print("No new plays since last watermark.")
        return

    payload["items"] = deduped


    now = datetime.now(timezone.utc)
    partition = now.strftime("year=%Y/month=%m/day=%d")
    base_path = Path("data/raw") / partition
    ensure_dir(base_path)

    out_file = base_path / f"recently_played_{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    write_json(payload, out_file)
    max_ms = max(played_at_to_ms(i["played_at"]) for i in deduped)
    save_watermark(watermark_path, max_ms)


    print(f"Wrote raw JSON to: {out_file}")


if __name__ == "__main__":
    main()
