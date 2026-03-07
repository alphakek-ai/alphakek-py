"""Tests for credential loading and storage."""

import json
import os
from pathlib import Path
from unittest.mock import patch

from alphakek._credentials import load_api_key, load_base_url, save_credentials


class TestLoadApiKey:
    def test_explicit_key_wins(self):
        assert load_api_key("alive_sk_explicit") == "alive_sk_explicit"

    def test_env_var_fallback(self):
        with patch.dict(os.environ, {"ALPHAKEK_API_KEY": "alive_sk_env"}):
            assert load_api_key() == "alive_sk_env"

    def test_explicit_beats_env(self):
        with patch.dict(os.environ, {"ALPHAKEK_API_KEY": "alive_sk_env"}):
            assert load_api_key("alive_sk_explicit") == "alive_sk_explicit"

    def test_file_fallback(self, tmp_path: Path):
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text(json.dumps({"api_key": "alive_sk_file"}))
        with patch("alphakek._credentials._CREDENTIALS_PATH", creds_file):
            assert load_api_key() == "alive_sk_file"

    def test_returns_none_when_nothing(self, tmp_path: Path):
        nonexistent = tmp_path / "nope.json"
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("alphakek._credentials._CREDENTIALS_PATH", nonexistent),
        ):
            # Remove ALPHAKEK_API_KEY if set
            os.environ.pop("ALPHAKEK_API_KEY", None)
            assert load_api_key() is None

    def test_handles_corrupt_file(self, tmp_path: Path):
        creds_file = tmp_path / "credentials.json"
        creds_file.write_text("not json at all")
        with patch("alphakek._credentials._CREDENTIALS_PATH", creds_file):
            assert load_api_key() is None


class TestSaveCredentials:
    def test_saves_and_loads(self, tmp_path: Path):
        creds_file = tmp_path / "config" / "alphakek" / "credentials.json"
        with patch("alphakek._credentials._CREDENTIALS_PATH", creds_file):
            path = save_credentials("alive_sk_test", agent_id="abc123")
            assert path == creds_file
            assert creds_file.exists()

            data = json.loads(creds_file.read_text())
            assert data["api_key"] == "alive_sk_test"
            assert data["agent_id"] == "abc123"

    def test_restricts_permissions(self, tmp_path: Path):
        creds_file = tmp_path / "credentials.json"
        with patch("alphakek._credentials._CREDENTIALS_PATH", creds_file):
            save_credentials("alive_sk_test")
            # Owner read/write only
            assert oct(creds_file.stat().st_mode)[-3:] == "600"


class TestLoadBaseUrl:
    def test_default_url(self):
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("ALPHAKEK_BASE_URL", None)
            assert load_base_url() == "https://alive-api.alphakek.ai"

    def test_explicit_url(self):
        assert load_base_url("http://localhost:8000") == "http://localhost:8000"

    def test_env_var_url(self):
        with patch.dict(os.environ, {"ALPHAKEK_BASE_URL": "https://staging.api.com"}):
            assert load_base_url() == "https://staging.api.com"

    def test_strips_trailing_slash(self):
        assert load_base_url("http://localhost:8000/") == "http://localhost:8000"
