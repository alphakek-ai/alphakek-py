"""Lambda commands: balance, transfer, transactions."""

from __future__ import annotations

import json
from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def balance(
    ctx: typer.Context,
) -> None:
    """Show current lambda balance and total earned."""
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))
    try:
        result = client.lambda_.balance()
    except httpx.HTTPStatusError as e:
        _api_error("Failed to get balance", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command()
def transfer(
    ctx: typer.Context,
    to: Annotated[str, typer.Option("--to", help="Recipient agent ID.")],
    amount: Annotated[float, typer.Option("--amount", help="Amount of lambda to transfer.")],
    metadata: Annotated[str | None, typer.Option("--metadata", help="Optional JSON metadata.")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run", help="Validate without executing transfer.")] = False,
    idempotency_key: Annotated[
        str | None, typer.Option("--idempotency-key", help="Idempotency key to prevent duplicate transfers.")
    ] = None,
) -> None:
    """Transfer lambda to another agent.

    Example::

        alphakek lambda transfer --to <agent_id> --amount 10.0
        alphakek lambda transfer --to <agent_id> --amount 5.0 --dry-run
    """
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    meta: dict | None = None
    if metadata:
        try:
            meta = json.loads(metadata)
        except json.JSONDecodeError as e:
            _error(f"Invalid JSON in --metadata: {e}")

    if amount <= 0:
        _error("--amount must be greater than 0.")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))
    try:
        result = client.lambda_.transfer(
            to=to,
            amount=amount,
            metadata=meta,
            dry_run=dry_run,
            idempotency_key=idempotency_key,
        )
    except httpx.HTTPStatusError as e:
        _api_error("Transfer failed", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)


@app.command()
def transactions(
    ctx: typer.Context,
    limit: Annotated[int, typer.Option("--limit", help="Max results.")] = 20,
    starting_after: Annotated[
        str | None, typer.Option("--starting-after", help="Cursor: UUID of last seen transaction.")
    ] = None,
    type_filter: Annotated[
        str | None,
        typer.Option("--type", help="Filter by type: purchase, query, refund, transfer_in, transfer_out, earn."),
    ] = None,
) -> None:
    """List lambda transaction history (audit trail).

    Example::

        alphakek lambda transactions
        alphakek lambda transactions --limit 50 --type query
    """
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))
    try:
        result = client.lambda_.transactions(
            limit=limit,
            starting_after=starting_after,
            type_filter=type_filter,
        )
    except httpx.HTTPStatusError as e:
        _api_error("Failed to get transactions", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
