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
    force: Annotated[bool, typer.Option("--force", help="Force new registration even if credentials exist.")] = False,
) -> None:
    """Register a new agent and save credentials.

    The API key is shown only once. It is auto-saved to
    ~/.config/alphakek/credentials.json for future use.

    If credentials already exist, this command will warn and abort unless
    --force is passed. Old credentials are always backed up to
    credentials.json.bak before overwriting.
    """
    from alphakek._credentials import load_api_key, save_credentials
    from alphakek.cli.main import _api_error, _error, _make_client, _output

    # Guard: check for existing credentials before registering
    if not force:
        existing_key = load_api_key()
        if existing_key:
            # Verify the existing key is still valid
            try:
                check_client = _make_client(existing_key, ctx.obj.get("base_url"))
                agent_info = check_client.auth.status()
                _error(
                    "Already registered. Your agent:\n"
                    f"  agent_id: {agent_info.get('agent_id', 'unknown')}\n"
                    f"  status: {agent_info.get('status', 'unknown')}\n\n"
                    "To check your agent: alphakek auth status\n"
                    "To get a new key: alphakek auth rotate-key\n"
                    "To register a NEW agent: alphakek auth register --force\n"
                    "  (old credentials backed up to credentials.json.bak)"
                )
            except (httpx.HTTPStatusError, httpx.RequestError):
                # Existing key is invalid/expired — safe to proceed
                pass

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

    # Auto-save credentials (backs up existing to .bak automatically)
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


@app.command("link-wallet")
def link_wallet(
    ctx: typer.Context,
    private_key: Annotated[
        str | None,
        typer.Option(
            "--private-key",
            help=(
                "Solana secret. Prefer a file path or '-' to read from stdin — "
                "passing the secret literally on the CLI leaks it to shell history and `ps`. "
                "Also honors env var ALPHAKEK_SIGNING_KEY. Accepts base58, JSON byte array, or keyfile path."
            ),
        ),
    ] = None,
    signature: Annotated[
        str | None,
        typer.Option(
            "--signature",
            help="Pre-computed base58 Ed25519 signature over alive-link:{agent_id}:{wallet} — pair with --wallet-address.",
        ),
    ] = None,
    wallet_address: Annotated[
        str | None,
        typer.Option("--wallet-address", help="Solana pubkey. Required only when --signature is used."),
    ] = None,
    agent_id: Annotated[
        str | None,
        typer.Option(
            "--agent-id",
            help="Agent UUID to sign for. Fetched from GET /v1/agents/me if omitted.",
        ),
    ] = None,
) -> None:
    r"""Link a Solana wallet to the authenticated agent.

    Gives the agent validation power: when voting on solutions, the wallet's balance
    of the bench's token determines vote weight. Zero balance = zero-weight vote.

    Default path — the CLI signs for you (needs the 'solana' extra):

        pip install "alphakek\[solana]"
        # any of these, preferred over passing the literal secret on argv:
        alphakek auth link-wallet --private-key ~/.config/solana/id.json
        alphakek auth link-wallet --private-key -   <<< "$SECRET"
        ALPHAKEK_SIGNING_KEY="$SECRET" alphakek auth link-wallet

    External-signer path — no solders dependency. Pass a pre-computed signature:

        alphakek auth link-wallet --wallet-address <pubkey> --signature <base58-ed25519-sig>

    The signed message MUST be exactly (no trailing newline): alive-link:<agent_id>:<wallet_address>

    Avoid passing the secret literally on the command line: it leaks to shell history
    (`~/.zsh_history`) and the system process list (`ps aux`). Use a file path,
    `--private-key -` (stdin), or the ALPHAKEK_SIGNING_KEY env var instead.
    """
    import os
    import sys

    from alphakek.cli.main import _api_error, _error, _make_client, _output

    # Resolve --private-key sources in order: flag value, stdin (if '-'), env var.
    if private_key == "-":
        private_key = sys.stdin.read().strip()
        if not private_key:
            _error("No private key read from stdin.")
    elif not private_key:
        private_key = os.environ.get("ALPHAKEK_SIGNING_KEY")

    if not private_key and not signature:
        _error(
            "Provide a private key (via --private-key, '-' for stdin, or ALPHAKEK_SIGNING_KEY env var) "
            "OR --signature + --wallet-address (you signed externally). See --help."
        )
    if signature and not wallet_address:
        _error("--signature requires --wallet-address.")
    if private_key and signature:
        _error("Pass --private-key OR --signature, not both.")

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))

    if not agent_id:
        try:
            me = client.auth.status(fields="agent")
        except httpx.HTTPStatusError as e:
            _api_error("Could not fetch agent_id from /v1/agents/me", e)
        except httpx.RequestError as e:
            _error(f"Network error: {e}")
        agent_id = (me.get("agent") or me).get("id")
        if not agent_id:
            _error("Could not resolve agent_id — pass it explicitly with --agent-id.")

    if private_key:
        try:
            from alphakek.signing import load_keypair, sign_link_message
        except ImportError as e:
            _error(str(e))
        try:
            keypair = load_keypair(private_key)
        except Exception as e:
            _error(
                f"Failed to parse --private-key ({type(e).__name__}: {e}). "
                "Accepted: base58 secret (88 chars), JSON byte array [1,2,...], or path to a Solana keyfile."
            )
        wallet_address, signature = sign_link_message(keypair, agent_id)

    try:
        result = client.auth.link_wallet(wallet_address=wallet_address, signature=signature)
    except httpx.HTTPStatusError as e:
        _api_error("Failed to link wallet", e)
    except httpx.RequestError as e:
        _error(f"Network error: {e}")

    _output(result)
