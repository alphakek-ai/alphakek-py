"""Bench commands: list and view."""

from __future__ import annotations

from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command("list")
def list_benches(
    ctx: typer.Context,
    tier: Annotated[
        str | None, typer.Option("--tier", help="Filter by quality tier: gold, silver, bronze, unranked.")
    ] = None,
    fields: Annotated[str | None, typer.Option("--fields", help="Comma-separated fields to return.")] = None,
) -> None:
    """List all active benches."""
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.bench.list(tier=tier, fields=fields)
    except httpx.HTTPStatusError as e:
        _api_error("Failed to list benches", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command()
def view(
    ctx: typer.Context,
    address: Annotated[str, typer.Argument(help="Bench token address.")],
    fields: Annotated[str | None, typer.Option("--fields", help="Comma-separated fields to return.")] = None,
) -> None:
    """View details for a specific bench."""
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.bench.view(address, fields=fields)
    except httpx.HTTPStatusError as e:
        _api_error("Bench not found", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
