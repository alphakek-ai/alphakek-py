"""Credential loading and storage.

Priority order (highest wins):
1. Explicit api_key parameter
2. ALPHAKEK_API_KEY environment variable
3. ~/.config/alphakek/credentials.json file
"""

from __future__ import annotations

import json
import os
from pathlib import Path

_CREDENTIALS_PATH = Path.home() / ".config" / "alphakek" / "credentials.json"


def load_api_key(explicit: str | None = None) -> str | None:
    """Load API key from the priority chain."""
    if explicit:
        return explicit

    env_key = os.environ.get("ALPHAKEK_API_KEY")
    if env_key:
        return env_key

    if _CREDENTIALS_PATH.exists():
        try:
            data = json.loads(_CREDENTIALS_PATH.read_text())
            return data.get("api_key")
        except (json.JSONDecodeError, OSError):
            return None

    return None


def save_credentials(api_key: str, **extra: str) -> Path:
    """Save credentials to ~/.config/alphakek/credentials.json.

    If credentials already exist, backs them up to credentials.json.bak
    before overwriting. This prevents accidental loss of API keys (and
    the λ balance associated with them).

    Returns the path where credentials were saved.
    """
    _CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Backup existing credentials before overwriting
    if _CREDENTIALS_PATH.exists():
        backup_path = _CREDENTIALS_PATH.with_suffix(".json.bak")
        try:
            import shutil

            shutil.copy2(_CREDENTIALS_PATH, backup_path)
            backup_path.chmod(0o600)
        except OSError:
            pass  # Best-effort backup — don't fail registration

    data = {"api_key": api_key, **extra}
    _CREDENTIALS_PATH.write_text(json.dumps(data, indent=2) + "\n")
    # Restrict permissions (owner-only read/write)
    _CREDENTIALS_PATH.chmod(0o600)
    return _CREDENTIALS_PATH


def load_base_url(explicit: str | None = None) -> str:
    """Load base URL with fallback to default."""
    if explicit:
        return explicit.rstrip("/")
    env_url = os.environ.get("ALPHAKEK_BASE_URL")
    if env_url:
        return env_url.rstrip("/")
    return "https://alive-api.alphakek.ai"
