import base64
from urllib.parse import urlencode

import requests


SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE = "https://api.spotify.com/v1"


class SpotifyClient:
    def __init__(self, client_id, client_secret, redirect_uri, scopes):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = scopes

    def auth_url(self):
        # Builds the login/consent URL for the user
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "scope": " ".join(self.scopes),
        }
        return f"{SPOTIFY_AUTH_URL}?{urlencode(params)}"

    def exchange_code_for_token(self, code):
        # Trades the authorization code for access + refresh tokens
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        resp = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def refresh_access_token(self, refresh_token):
        # Refreshes an expired access token without re-login
        auth_header = base64.b64encode(
            f"{self.client_id}:{self.client_secret}".encode()
        ).decode()
        headers = {"Authorization": f"Basic {auth_header}"}
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }
        resp = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_recently_played(self, access_token, limit=50, after_ms=None):
        # Pulls recent listening events
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"limit": limit}
        if after_ms:
            params["after"] = after_ms
        url = f"{SPOTIFY_API_BASE}/me/player/recently-played"
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
