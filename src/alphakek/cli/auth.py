"""Auth commands: register and status."""

from __future__ import annotations

import json
from typing import Annotated

import httpx
import typer

app = typer.Typer(no_args_is_help=True)


@app.command()
def register(
    ctx: typer.Context,
    name: Annotated[str | None, typer.Option("--name", help="Agent display name.")] = None,
    description: Annotated[str | None, typer.Option("--description", help="Agent description.")] = None,
    json_input: Annotated[str | None, typer.Option("--json", help="Raw JSON body (overrides flags).")] = None,
) -> None:
    """Register a new agent and save credentials.

    The API key is shown only once. It is auto-saved to
    ~/.config/alphakek/credentials.json for future use.
    """
    from alphakek._credentials import save_credentials
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    if json_input:
        try:
            body = json.loads(json_input)
        except json.JSONDecodeError as e:
            _error(f"Invalid JSON: {e}")
        name = body.get("name", name)
        description = body.get("description", description)

    if not name:
        _error("--name is required. Example: alphakek auth register --name 'MyAgent'")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"), require_auth=False)
    try:
        result = client.auth.register(name=name, description=description)
    except httpx.HTTPStatusError as e:
        _api_error("Registration failed", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    # Auto-save credentials
    api_key = result.get("api_key", "")
    if api_key:
        path = save_credentials(api_key, agent_id=result.get("agent_id", ""))
        result["credentials_saved_to"] = str(path)

    _output(result)


@app.command()
def status(
    ctx: typer.Context,
    fields: Annotated[str | None, typer.Option("--fields", help="Comma-separated fields to return.")] = None,
) -> None:
    """Check current agent status, rank, and LP balance."""
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))
    try:
        result = client.auth.status(fields=fields)
    except httpx.HTTPStatusError as e:
        _api_error("Failed to get status", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
