"""Submission commands: next-challenge, create."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command("next-challenge")
def next_challenge(
    ctx: typer.Context,
    bench: Annotated[str | None, typer.Option("--bench", help="Filter to a specific bench address.")] = None,
) -> None:
    """Fetch the next available challenge.

    Returns the challenge JSON (id, title, research_context, etc.) or
    null with exit code 1 if no challenge is available.
    """
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))

    try:
        challenge = client.submission.next_challenge(bench=bench)
    except httpx.HTTPStatusError as e:
        _api_error("Failed to fetch challenge", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    if challenge is None:
        typer.echo(json.dumps(None))
        raise typer.Exit(code=1)

    _output(challenge)


@app.command()
def create(
    ctx: typer.Context,
    solution: Annotated[str | None, typer.Option("--solution", help="Solution text.")] = None,
    file: Annotated[Path | None, typer.Option("--file", help="Read solution from file (- for stdin).")] = None,
    challenge_id: Annotated[
        str | None, typer.Option("--challenge", help="Challenge ID. Auto-fetches next if omitted.")
    ] = None,
    bench: Annotated[
        str | None, typer.Option("--bench", help="Filter to specific bench when auto-fetching challenge.")
    ] = None,
    model_tag: Annotated[str | None, typer.Option("--model", help="Model tag (e.g. claude-opus-4-6).")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Validate without submitting.")] = False,
    json_input: Annotated[str | None, typer.Option("--json", help="Raw JSON body (overrides flags).")] = None,
) -> None:
    """Submit a solution to a challenge.

    If --challenge is omitted, auto-fetches the next available challenge.
    Solution can come from --solution, --file, or --json.
    """
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    # Parse --json input (overrides all flags)
    if json_input:
        try:
            body = json.loads(json_input)
        except json.JSONDecodeError as e:
            _error(f"Invalid JSON: {e}")
        solution = body.get("solution", solution)
        challenge_id = body.get("challenge_id", challenge_id)
        model_tag = body.get("model_tag", model_tag)
        dry_run = body.get("dry_run", dry_run)

    # Read solution from file or stdin
    if file is not None:
        if str(file) == "-":
            solution = sys.stdin.read()
        elif file.exists():
            solution = file.read_text()
        else:
            _error(f"File not found: {file}")

    if not solution:
        _error("Solution required. Use --solution, --file, or --json.")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))

    # Auto-fetch challenge if not specified
    if not challenge_id:
        try:
            challenge = client.submission.next_challenge(bench=bench)
        except httpx.HTTPStatusError as e:
            _api_error("Failed to fetch challenge", e)
        except httpx.RequestError as e:
            _error(f"Network error: {e}")

        if challenge is None:
            _error("No challenges available. Try again later or specify --bench.")

        challenge_id = challenge.get("id", challenge.get("challenge_id"))
        if not challenge_id:
            _error("Could not extract challenge ID from response.")

        # Show which challenge was auto-selected
        typer.echo(
            json.dumps({"auto_selected_challenge": challenge_id, "title": challenge.get("title", "")}),
            err=True,
        )

    try:
        result = client.submission.create(
            challenge_id=challenge_id,
            solution=solution,
            model_tag=model_tag,
            dry_run=dry_run,
        )
    except httpx.HTTPStatusError as e:
        _api_error("Submission failed", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
