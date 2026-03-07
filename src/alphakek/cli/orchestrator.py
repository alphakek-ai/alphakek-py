"""Orchestrator commands: evaluate, list, info."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def evaluate(
    ctx: typer.Context,
    bench: Annotated[str | None, typer.Option("--bench", help="Bench token address.")] = None,
    content: Annotated[str | None, typer.Option("--content", help="Content to evaluate.")] = None,
    file: Annotated[Path | None, typer.Option("--file", help="Read content from file (- for stdin).")] = None,
    context: Annotated[str | None, typer.Option("--context", help="Optional evaluation context.")] = None,
    fields: Annotated[str | None, typer.Option("--fields", help="Comma-separated fields to return.")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Validate without deducting LP.")] = False,
    json_input: Annotated[str | None, typer.Option("--json", help="Raw JSON body (overrides flags).")] = None,
) -> None:
    """Evaluate content using a bench's trained Orchestrator.

    Costs LP per query. Use --dry-run to check balance without deducting.
    """
    from alphakek.cli.main import _error, _make_client, _output

    if json_input:
        try:
            body = json.loads(json_input)
        except json.JSONDecodeError as e:
            _error(f"Invalid JSON: {e}")
        bench = body.get("token_address", body.get("bench", bench))
        content = body.get("content", content)
        context = body.get("context", context)
        fields = body.get("fields", fields)
        dry_run = body.get("dry_run", dry_run)

    # Read content from file or stdin
    if file is not None:
        if str(file) == "-":
            content = sys.stdin.read()
        elif file.exists():
            content = file.read_text()
        else:
            _error(f"File not found: {file}")

    if not bench:
        _error("--bench is required. Pass the bench token address.")

    if not content:
        _error("Content required. Use --content, --file, or --json.")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))
    try:
        result = client.orchestrator.evaluate(
            bench=bench,
            content=content,
            context=context,
            fields=fields,
            dry_run=dry_run,
        )
    except httpx.HTTPStatusError as e:
        _error(f"Evaluation failed: {e.response.text}")
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command("list")
def list_orchestrators(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit", help="Max results.")] = 50,
    offset: Annotated[int, typer.Option("--offset", help="Pagination offset.")] = 0,
) -> None:
    """List all available Orchestrators."""
    from alphakek.cli.main import _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.orchestrator.list(limit=limit, offset=offset)
    except httpx.HTTPStatusError as e:
        _error(f"Failed to list orchestrators: {e.response.text}")
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command()
def info(
    ctx: typer.Context,
    bench: Annotated[str, typer.Argument(help="Bench token address.")],
) -> None:
    """Get metadata about a specific bench's Orchestrator."""
    from alphakek.cli.main import _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.orchestrator.info(bench)
    except httpx.HTTPStatusError as e:
        _error(f"Orchestrator not found: {e.response.text}")
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
