"""Validation commands: next, submit."""

from __future__ import annotations

import json
from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command("next")
def next_pair(
    ctx: typer.Context,
    bench: Annotated[str | None, typer.Option("--bench", help="Filter to a specific bench address.")] = None,
) -> None:
    """Fetch the next pair of solutions to validate.

    Returns the pair JSON (challenge, solution_a, solution_b) on exit 0.
    When no pair is available (HTTP 204), prints ``null`` and exits with
    code 2 — distinct from the generic error code 1 so scripts can tell
    "queue is empty" from "auth/network broke".
    """
    from alphakek.cli.main import EXIT_NO_DATA, _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))

    try:
        pair = client.validation.next_pair(bench=bench)
    except httpx.HTTPStatusError as e:
        _api_error("Failed to fetch validation pair", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    if pair is None:
        typer.echo(json.dumps(None))
        raise typer.Exit(code=EXIT_NO_DATA)

    _output(pair)


@app.command()
def submit(
    ctx: typer.Context,
    winner: Annotated[str, typer.Option("--winner", help="Vote choice: 'a', 'b', or 'skip'.")],
    challenge_id: Annotated[
        str | None, typer.Option("--challenge", help="Challenge ID. Auto-fetches next if omitted.")
    ] = None,
    solution_a_id: Annotated[str | None, typer.Option("--solution-a", help="Solution A ID.")] = None,
    solution_b_id: Annotated[str | None, typer.Option("--solution-b", help="Solution B ID.")] = None,
    bench: Annotated[
        str | None, typer.Option("--bench", help="Filter to specific bench when auto-fetching pair.")
    ] = None,
    json_input: Annotated[str | None, typer.Option("--json", help="Raw JSON body (overrides flags).")] = None,
) -> None:
    """Submit a validation vote on a pair of solutions.

    If --challenge, --solution-a, --solution-b are omitted, auto-fetches
    the next available pair. You only need to provide --winner.
    """
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    if json_input:
        try:
            body = json.loads(json_input)
        except json.JSONDecodeError as e:
            _error(f"Invalid JSON: {e}")
        challenge_id = body.get("challenge_id", challenge_id)
        solution_a_id = body.get("solution_a_id", solution_a_id)
        solution_b_id = body.get("solution_b_id", solution_b_id)
        winner = body.get("winner", winner)

    if winner not in ("a", "b", "skip"):
        _error("--winner must be 'a', 'b', or 'skip'.")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))

    # Auto-fetch pair if IDs not provided
    if not all([challenge_id, solution_a_id, solution_b_id]):
        try:
            pair = client.validation.next_pair(bench=bench)
        except httpx.HTTPStatusError as e:
            _api_error("Failed to fetch validation pair", e)
        except httpx.RequestError as e:
            _error(f"Network error: {e}")

        if pair is None:
            _error("No validation pairs available. Try again later or specify --bench.")

        challenge_id = pair["challenge_id"]
        solution_a_id = pair["solution_a_id"]
        solution_b_id = pair["solution_b_id"]

        typer.echo(
            json.dumps(
                {
                    "auto_selected_pair": challenge_id,
                    "title": pair.get("challenge_title", ""),
                }
            ),
            err=True,
        )

    try:
        result = client.validation.submit(
            challenge_id=challenge_id,
            solution_a_id=solution_a_id,
            solution_b_id=solution_b_id,
            winner=winner,
        )
    except httpx.HTTPStatusError as e:
        _api_error("Validation failed", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
