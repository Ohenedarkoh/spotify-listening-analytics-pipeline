import json
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from spotify_client import SpotifyClient


def ensure_dir(path: Path):
    # Create partition directory if it doesn't exist
    path.mkdir(parents=True, exist_ok=True)


def write_json(payload, out_path: Path):
    # Persist raw payload exactly as received
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def main():
    # Load local secrets (do not commit configs/.env)
    load_dotenv("configs/.env")

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
    payload = client.get_recently_played(access_token=access_token, limit=50)

    now = datetime.now(timezone.utc)
    partition = now.strftime("year=%Y/month=%m/day=%d")
    base_path = Path("data/raw") / partition
    ensure_dir(base_path)

    out_file = base_path / f"recently_played_{now.strftime('%Y%m%dT%H%M%SZ')}.json"
    write_json(payload, out_file)

    print(f"Wrote raw JSON to: {out_file}")


if __name__ == "__main__":
    main()
