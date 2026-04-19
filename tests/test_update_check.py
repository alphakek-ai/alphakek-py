"""Tests for the best-effort update-check notifier."""

from __future__ import annotations

import json
import time
from unittest.mock import MagicMock, patch

import pytest

from alphakek import _update_check


@pytest.fixture(autouse=True)
def isolate_cache(tmp_path, monkeypatch):
    """Redirect the cache file into a per-test tmp dir."""
    monkeypatch.setattr(_update_check, "_CACHE_PATH", tmp_path / "update_check.json")
    yield


class TestScheduleUpdateCheck:
    def test_skipped_when_env_opt_out(self, monkeypatch):
        monkeypatch.setenv("ALPHAKEK_NO_UPDATE_CHECK", "1")
        with patch("atexit.register") as reg:
            _update_check.schedule_update_check("0.5.0")
            reg.assert_not_called()

    @pytest.mark.parametrize("ci_var", _update_check._CI_VARS)
    def test_skipped_in_ci(self, monkeypatch, ci_var):
        # Clear any other CI markers set by the test runner, then flip only this one.
        for v in _update_check._CI_VARS:
            monkeypatch.delenv(v, raising=False)
        monkeypatch.delenv("ALPHAKEK_NO_UPDATE_CHECK", raising=False)
        monkeypatch.setenv(ci_var, "true")
        with patch("atexit.register") as reg:
            _update_check.schedule_update_check("0.5.0")
            reg.assert_not_called()

    def test_skipped_when_stderr_not_tty(self, monkeypatch):
        for v in _update_check._CI_VARS:
            monkeypatch.delenv(v, raising=False)
        monkeypatch.delenv("ALPHAKEK_NO_UPDATE_CHECK", raising=False)
        with patch("sys.stderr") as stderr:
            stderr.isatty.return_value = False
            with patch("atexit.register") as reg:
                _update_check.schedule_update_check("0.5.0")
                reg.assert_not_called()

    def test_registered_when_interactive_tty(self, monkeypatch):
        for v in _update_check._CI_VARS:
            monkeypatch.delenv(v, raising=False)
        monkeypatch.delenv("ALPHAKEK_NO_UPDATE_CHECK", raising=False)
        with patch("sys.stderr") as stderr:
            stderr.isatty.return_value = True
            with patch("atexit.register") as reg:
                _update_check.schedule_update_check("0.5.0")
                reg.assert_called_once()


class TestCheckAndEmit:
    def test_emits_banner_when_newer_available(self, capsys):
        # Populate fresh cache so no network call needed.
        _update_check._write_cache({"checked_at": time.time(), "latest": "0.6.0"})
        _update_check._check_and_emit("0.5.0")
        captured = capsys.readouterr()
        assert "0.6.0" in captured.err
        assert "0.5.0" in captured.err
        assert "pip install -U alphakek" in captured.err

    def test_silent_when_current_matches_latest(self, capsys):
        _update_check._write_cache({"checked_at": time.time(), "latest": "0.5.0"})
        _update_check._check_and_emit("0.5.0")
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_silent_when_local_is_newer_than_pypi(self, capsys):
        # E.g. editable install from git that's ahead of PyPI.
        _update_check._write_cache({"checked_at": time.time(), "latest": "0.4.0"})
        _update_check._check_and_emit("0.5.0")
        captured = capsys.readouterr()
        assert captured.err == ""

    def test_silent_on_network_failure(self, capsys):
        # No cache file present; urlopen mocked to raise.
        with patch("urllib.request.urlopen", side_effect=OSError("network down")):
            _update_check._check_and_emit("0.5.0")
        captured = capsys.readouterr()
        assert captured.err == ""


class TestGetLatestVersion:
    def test_uses_cache_when_fresh(self):
        _update_check._write_cache({"checked_at": time.time(), "latest": "0.9.9"})
        with patch("urllib.request.urlopen") as u:
            result = _update_check._get_latest_version()
            u.assert_not_called()
        assert result == "0.9.9"

    def test_refetches_when_cache_stale(self):
        _update_check._write_cache(
            {"checked_at": time.time() - 2 * _update_check._CACHE_TTL_SECONDS, "latest": "0.1.0"}
        )
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"info": {"version": "0.7.0"}}).encode()
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_response):
            result = _update_check._get_latest_version()
        assert result == "0.7.0"
        # Cache refreshed
        assert json.loads(_update_check._CACHE_PATH.read_text())["latest"] == "0.7.0"

    def test_returns_none_on_malformed_response(self):
        mock_response = MagicMock()
        mock_response.read.return_value = b"not json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        with patch("urllib.request.urlopen", return_value=mock_response):
            assert _update_check._get_latest_version() is None


class TestIsNewer:
    def test_standard_semver(self):
        assert _update_check._is_newer("0.6.0", "0.5.0")
        assert _update_check._is_newer("1.0.0", "0.99.99")
        assert not _update_check._is_newer("0.5.0", "0.6.0")
        assert not _update_check._is_newer("0.5.0", "0.5.0")

    def test_patch_versions(self):
        assert _update_check._is_newer("0.5.1", "0.5.0")
        assert not _update_check._is_newer("0.5.0", "0.5.1")

    def test_prerelease_handling(self):
        # With packaging installed, these follow PEP 440 semantics.
        assert _update_check._is_newer("0.6.0", "0.6.0rc1")
