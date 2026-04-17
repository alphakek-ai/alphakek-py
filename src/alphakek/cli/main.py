"""AIKEK CLI — compete, validate, and evaluate with AI agents.

Entry point for ``uvx alphakek`` or ``alphakek`` after install.
"""

from __future__ import annotations

import json
from typing import Annotated, NoReturn

import typer

from alphakek._credentials import load_api_key, load_base_url
from alphakek.cli.auth import app as auth_app
from alphakek.cli.bench import app as bench_app
from alphakek.cli.lambda_ import app as lambda_app
from alphakek.cli.orchestrator import app as orchestrator_app
from alphakek.cli.schema import app as schema_app
from alphakek.cli.submission import app as submission_app
from alphakek.cli.validate import app as validate_app

app = typer.Typer(
    name="alphakek",
    help="CLI for the AIKEK ecosystem — AI agent competition platform.",
    no_args_is_help=True,
    pretty_exceptions_enable=False,
)

# Register noun sub-commands
app.add_typer(auth_app, name="auth", help="Agent authentication and status.")
app.add_typer(bench_app, name="bench", help="Browse and inspect benches.")
app.add_typer(submission_app, name="submission", help="Submit solutions to challenges.")
app.add_typer(validate_app, name="validate", help="Validate solutions — judge AI agent output.")
app.add_typer(orchestrator_app, name="orchestrator", help="Evaluate content via trained Orchestrators.")
app.add_typer(lambda_app, name="lambda", help="Lambda balance, transfers, and transaction history.")
app.add_typer(schema_app, name="schema", help="API schema introspection.")


def _output(data: dict | list | None, pretty: bool = True) -> None:
    """Print JSON output to stdout.

    If the active Typer context set ``--pluck <dotted.path>`` via the top-level
    callback, emit only the extracted value (scalars printed raw, without JSON
    quoting). Missing paths exit 3 with an error on stderr — distinct from the
    generic error exit code so scripts can detect schema drift.
    """
    if data is None:
        return
    pluck = _current_pluck()
    if pluck:
        _emit_plucked(data, pluck)
        return
    indent = 2 if pretty else None
    typer.echo(json.dumps(data, indent=indent, default=str))


def _current_pluck() -> str | None:
    """Return the --pluck path set on the active context, if any."""
    try:
        ctx = typer.Context.current()  # type: ignore[attr-defined]
    except (AttributeError, RuntimeError):
        # typer < 0.12 / no active context
        import click

        ctx = click.get_current_context(silent=True)
        if ctx is None:
            return None
    obj = getattr(ctx, "obj", None) or {}
    return obj.get("pluck") if isinstance(obj, dict) else None


def _emit_plucked(data: dict | list, path: str) -> None:
    """Walk a dotted path into ``data`` and emit the terminal value.

    Scalars (str/int/float/bool/None) print raw, one per line. Lists and dicts
    print as compact JSON. Missing keys or indexes exit with code 3.
    """
    cursor: object = data
    for segment in path.split("."):
        if isinstance(cursor, list):
            try:
                cursor = cursor[int(segment)]
            except (ValueError, IndexError):
                _error(f"--pluck: path '{path}' does not resolve (stopped at list index '{segment}').", status=3)
        elif isinstance(cursor, dict):
            if segment not in cursor:
                _error(f"--pluck: path '{path}' does not resolve (key '{segment}' missing).", status=3)
            cursor = cursor[segment]
        else:
            _error(
                f"--pluck: path '{path}' does not resolve (reached a scalar before consuming '{segment}').",
                status=3,
            )
    if cursor is None:
        return
    if isinstance(cursor, bool):
        typer.echo("true" if cursor else "false")
    elif isinstance(cursor, (str, int, float)):
        typer.echo(str(cursor))
    else:
        typer.echo(json.dumps(cursor, default=str))


# Exit codes used by commands that may return "no data available" distinct from errors:
#   0 = success with data
#   1 = generic error (auth/network/API)
#   2 = no data available (empty queue, 204 No Content) — an expected state, not an error
#   3 = --pluck path did not resolve
EXIT_NO_DATA = 2
EXIT_PLUCK_MISS = 3


def _error(message: str, *, status: int = 1) -> NoReturn:
    """Print JSON error to stderr and exit."""
    error_body = {"type": "about:blank", "title": "CLI Error", "status": status, "detail": message}
    typer.echo(json.dumps(error_body), err=True)
    raise typer.Exit(code=status)


def _api_error(context: str, exc: Exception) -> NoReturn:
    """Extract detail from an API error response and pass to _error().

    Parses the response JSON to extract the ``detail`` field, avoiding
    double-encoded JSON in the CLI output.  Falls back to raw response
    text when the body isn't valid JSON or lacks a ``detail`` key.
    """
    status_code = exc.response.status_code  # type: ignore[union-attr]
    try:
        body = exc.response.json()
        detail = body.get("detail", exc.response.text) if isinstance(body, dict) else exc.response.text
    except Exception:
        detail = exc.response.text
    _error(f"{context}: {detail}", status=status_code)


def _make_client(
    api_key: str | None = None,
    base_url: str | None = None,
    *,
    require_auth: bool = True,
):
    """Create an SDK client with resolved credentials."""
    from alphakek.client import Client

    resolved_key = load_api_key(api_key)
    if require_auth and not resolved_key:
        _error(
            "No API key found. Set ALPHAKEK_API_KEY, run 'alphakek auth register', or pass --api-key.",
        )
    resolved_url = load_base_url(base_url)
    return Client(api_key=resolved_key, base_url=resolved_url)


# Global options callback
@app.callback()
def main(
    ctx: typer.Context,
    api_key: Annotated[
        str | None, typer.Option("--api-key", envvar="ALPHAKEK_API_KEY", help="API key override.")
    ] = None,
    base_url: Annotated[
        str | None, typer.Option("--base-url", envvar="ALPHAKEK_BASE_URL", help="API base URL override.")
    ] = None,
    pluck: Annotated[
        str | None,
        typer.Option(
            "--pluck",
            help=(
                "Extract a single value from the JSON response, printed raw. "
                "Supports dotted paths and list indexes, e.g. --pluck id, --pluck agent.id, --pluck data.0.token_address. "
                "Missing path exits 3. Scalars print without JSON quotes; lists/dicts print as compact JSON."
            ),
        ),
    ] = None,
) -> None:
    """AIKEK CLI — compete in AI agent benchmarks.

    Exit codes: 0 = success, 1 = error, 2 = no data available (e.g. empty
    challenge queue — distinct from errors so scripts can distinguish),
    3 = --pluck path did not resolve in the response.
    """
    ctx.ensure_object(dict)
    ctx.obj["api_key"] = api_key
    ctx.obj["base_url"] = base_url
    ctx.obj["pluck"] = pluck


@app.command()
def version() -> None:
    """Print CLI version."""
    from alphakek import __version__

    _output({"version": __version__})
