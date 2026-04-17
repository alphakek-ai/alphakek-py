"""Best-effort "new version available" notifier.

Design goals:
- Never block the user's command: runs via ``atexit`` with a 1s network timeout.
- Never pollute scripts: only emits to stderr when stderr is a tty (humans),
  respecting ``ALPHAKEK_NO_UPDATE_CHECK`` and common CI env vars.
- Never crash: all failures (network, parse, filesystem, permissions) are silent.
- Minimize chatter: caches result for 24 hours in the existing alphakek config dir.
"""

from __future__ import annotations

import atexit
import json
import os
import sys
import time
from pathlib import Path

_CACHE_TTL_SECONDS = 24 * 3600
_PYPI_TIMEOUT_SECONDS = 1.0
_CACHE_PATH = Path.home() / ".config" / "alphakek" / "update_check.json"
_CI_VARS = ("CI", "GITHUB_ACTIONS", "GITLAB_CI", "BUILDKITE", "CIRCLECI", "TRAVIS")


def schedule_update_check(current_version: str) -> None:
    """Register a post-command update check, if appropriate for the environment."""
    if os.environ.get("ALPHAKEK_NO_UPDATE_CHECK"):
        return
    if any(os.environ.get(v) for v in _CI_VARS):
        return
    # Only notify humans — agents piping stderr shouldn't see the banner.
    try:
        if not sys.stderr.isatty():
            return
    except (AttributeError, ValueError):
        return
    atexit.register(_check_and_emit, current_version)


def _check_and_emit(current_version: str) -> None:
    """Called at process exit. All exceptions swallowed — this is best-effort."""
    try:
        latest = _get_latest_version()
        if latest and _is_newer(latest, current_version):
            sys.stderr.write(
                f"\nalphakek {latest} is available (you have {current_version}). Upgrade: pip install -U alphakek\n"
            )
    except Exception:  # noqa: S110 — best-effort notifier must never break the user's command
        pass


def _get_latest_version() -> str | None:
    """Return the latest alphakek version from cache or PyPI. None on failure."""
    now = time.time()
    cached = _read_cache()
    if cached and now - cached.get("checked_at", 0) < _CACHE_TTL_SECONDS:
        v = cached.get("latest")
        return v if isinstance(v, str) else None

    import urllib.request

    try:
        with urllib.request.urlopen(
            "https://pypi.org/pypi/alphakek/json",
            timeout=_PYPI_TIMEOUT_SECONDS,
        ) as response:
            data = json.loads(response.read())
    except Exception:
        return None

    latest = data.get("info", {}).get("version") if isinstance(data, dict) else None
    if isinstance(latest, str):
        _write_cache({"checked_at": now, "latest": latest})
    return latest


def _read_cache() -> dict | None:
    try:
        return json.loads(_CACHE_PATH.read_text())
    except (FileNotFoundError, json.JSONDecodeError, PermissionError, OSError):
        return None


def _write_cache(payload: dict) -> None:
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(payload))
    except (PermissionError, OSError):
        pass


def _is_newer(latest: str, current: str) -> bool:
    """Compare semver-like versions, falling back to tuple-of-ints on parse failure."""
    try:
        from packaging.version import Version

        return Version(latest) > Version(current)
    except ImportError:
        pass
    except Exception:
        return False

    def _tuple(v: str) -> tuple[int, ...]:
        parts: list[int] = []
        for segment in v.split("."):
            digits = "".join(c for c in segment if c.isdigit())
            parts.append(int(digits) if digits else 0)
        return tuple(parts)

    try:
        return _tuple(latest) > _tuple(current)
    except Exception:
        return False
