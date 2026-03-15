"""Orchestrator commands: query, list, info."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def query(
    ctx: typer.Context,
    bench: Annotated[str | None, typer.Option("--bench", help="Bench token address (single-token shorthand).")] = None,
    content: Annotated[
        str | None, typer.Option("--content", help="Content to evaluate (single-candidate shorthand).")
    ] = None,
    file: Annotated[Path | None, typer.Option("--file", help="Read content from file (- for stdin).")] = None,
    prompt: Annotated[str, typer.Option("--prompt", help="Context about the evaluation task.")] = "",
    effort: Annotated[str, typer.Option("--effort", help="Thinking depth: low | medium | high.")] = "high",
    fields: Annotated[str | None, typer.Option("--fields", help="Comma-separated fields to return.")] = None,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Validate and check balance without deducting lambda.")
    ] = False,
    json_input: Annotated[str | None, typer.Option("--json", help="Raw JSON body (overrides flags).")] = None,
) -> None:
    """Evaluate content against a bench's trained Orchestrator.

    Costs lambda per query. Use --dry-run to check balance without deducting.

    Simple usage (single candidate, single bench)::

        alphakek orchestrator query --bench <addr> --content "my solution"

    Read from file::

        alphakek orchestrator query --bench <addr> --file solution.txt

    Batch (via --json for full request control)::

        alphakek orchestrator query --json '{"candidates":[...],"tokens":[...]}'

    Response shape: results[].candidates[] with score, analysis, backpressure fields.
    For single-bench queries: results[0].candidates[0] has your score.
    """
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    candidates: list[str] = []
    tokens: list[str] = []

    if json_input:
        try:
            body = json.loads(json_input)
        except json.JSONDecodeError as e:
            _error(f"Invalid JSON: {e}")

        # Accept full new shape or legacy flat fields
        raw_candidates = body.get("candidates", [])
        if raw_candidates:
            candidates = [c["content"] if isinstance(c, dict) else c for c in raw_candidates]
        raw_tokens = body.get("tokens", [])
        if raw_tokens:
            tokens = [t["address"] if isinstance(t, dict) else t for t in raw_tokens]

        # Legacy flat field fallback
        if not candidates:
            legacy_content = body.get("content", content)
            if legacy_content:
                candidates = [legacy_content]
        if not tokens:
            legacy_bench = body.get("token_address", body.get("bench", bench))
            if legacy_bench:
                tokens = [legacy_bench]

        prompt = body.get("prompt", body.get("context", prompt))
        effort = body.get("effort", effort)
        fields = body.get("fields", fields)
        dry_run = body.get("dry_run", dry_run)

    # Read content from file or stdin (overrides --content)
    if file is not None:
        if str(file) == "-":
            file_content = sys.stdin.read()
        elif file.exists():
            file_content = file.read_text()
        else:
            _error(f"File not found: {file}")
        candidates = [file_content]

    # Single-candidate shorthand: --content
    if content and not candidates:
        candidates = [content]

    # Single-token shorthand: --bench
    if bench and not tokens:
        tokens = [bench]

    if not candidates:
        _error("Content required. Use --content, --file, or --json.")

    if not tokens:
        _error("--bench is required. Pass the bench token address.")

    if effort not in ("low", "medium", "high"):
        _error("--effort must be one of: low, medium, high")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))
    try:
        result = client.orchestrator.query(
            candidates=candidates,
            tokens=tokens,
            prompt=prompt,
            effort=effort,
            fields=fields,
            dry_run=dry_run,
        )
    except httpx.HTTPStatusError as e:
        _api_error("Query failed", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command("list")
def list_orchestrators(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit", help="Max results.")] = 50,
) -> None:
    """List all available Orchestrators."""
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.orchestrator.list(limit=limit)
    except httpx.HTTPStatusError as e:
        _api_error("Failed to list orchestrators", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command()
def info(
    ctx: typer.Context,
    bench: Annotated[str, typer.Argument(help="Bench token address.")],
) -> None:
    """Get metadata about a specific bench's Orchestrator."""
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.orchestrator.info(bench)
    except httpx.HTTPStatusError as e:
        _api_error("Orchestrator not found", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
