import json
import os
from pathlib import Path

_LOCAL_PATH = Path(__file__).resolve().parents[2] / 'secrets' / 'google_credentials.json'


def load_google_credentials_dict():
    """Return Google service-account credentials as a parsed dict.

    Prefers the GOOGLE_CREDENTIALS env var (used by GitHub Actions) containing
    the JSON as a string. Falls back to the gitignored local file at
    secrets/google_credentials.json for local development.
    """
    env = os.environ.get('GOOGLE_CREDENTIALS')
    if env:
        return json.loads(env)
    if _LOCAL_PATH.exists():
        return json.loads(_LOCAL_PATH.read_text())
    raise RuntimeError(
        "No Google credentials found. Set the GOOGLE_CREDENTIALS env var or "
        f"place the service-account JSON at {_LOCAL_PATH}."
    )
