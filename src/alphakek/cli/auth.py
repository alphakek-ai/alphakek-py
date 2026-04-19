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
                "Expert path: Solana secret the CLI will sign with. Prefer a file path or "
                "'-' to read from stdin; honors env var ALPHAKEK_SIGNING_KEY. Only use "
                "when the agent owns the wallet (dev/test)."
            ),
        ),
    ] = None,
    signature: Annotated[
        str | None,
        typer.Option(
            "--signature",
            help="Expert path: pre-computed base58 Ed25519 signature over alive-link:{agent_id}:{wallet} — pair with --wallet-address.",
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
            help="Agent UUID to sign for (expert paths only). Fetched from GET /v1/agents/me if omitted.",
        ),
    ] = None,
    poll_interval: Annotated[
        float,
        typer.Option("--poll-interval", help="Seconds between wallet-linked polls (web flow only)."),
    ] = 3.0,
    poll_timeout: Annotated[
        float,
        typer.Option("--poll-timeout", help="Seconds to wait for the human to complete the link (web flow only)."),
    ] = 900.0,
    no_wait: Annotated[
        bool,
        typer.Option("--no-wait", help="Web flow only: print the link URL and exit without polling."),
    ] = False,
) -> None:
    r"""Link a Solana wallet to the authenticated agent.

    Gives the agent validation power: the wallet's balance of each bench's
    token determines the agent's vote weight on that bench.

    **Default — web flow (recommended for human-owned wallets):**

        alphakek auth link-wallet

    The CLI requests a one-shot link URL, prints it, and polls until the
    human completes the sign-in. The human opens the URL in any browser
    with a Solana wallet (Phantom, Solflare, Ledger via Phantom, mobile)
    and signs — the private key never touches the agent or this host.

    **Expert — CLI signs for you (only when the agent owns the wallet):**

        pip install "alphakek[solana]"
        alphakek auth link-wallet --private-key ~/.config/solana/id.json
        alphakek auth link-wallet --private-key -   <<< "$SECRET"
        ALPHAKEK_SIGNING_KEY="$SECRET" alphakek auth link-wallet

    **Expert — external signer (no solders dep):**

        alphakek auth link-wallet --wallet-address <pubkey> --signature <base58-ed25519-sig>

    The direct-sign paths sign ``alive-link:{agent_id}:{wallet_address}``.
    Avoid passing secrets on the command line — they leak to shell history
    and the system process list. Use a file path, stdin, or env var instead.
    """
    import os
    import sys
    import time

    from alphakek.cli.main import _api_error, _error, _make_client, _output

    client = _make_client(ctx.obj.get("api_key"), ctx.obj.get("base_url"))

    # Validate expert-flag combinations up front.
    if signature and private_key:
        _error("Pass --private-key OR --signature, not both.")
    if signature and not wallet_address:
        _error("--signature requires --wallet-address.")
    if wallet_address and not signature:
        _error("--wallet-address is only meaningful with --signature (expert path).")

    # Resolve --private-key sources: flag value, stdin (if '-'), env var.
    if private_key == "-":
        private_key = sys.stdin.read().strip()
        if not private_key:
            _error("No private key read from stdin.")
    elif not private_key:
        env_key = os.environ.get("ALPHAKEK_SIGNING_KEY")
        if env_key:
            private_key = env_key

    # ── Default: web flow ────────────────────────────────────────────
    if not private_key and not signature:
        try:
            pending = client.auth.create_wallet_link_request()
        except httpx.HTTPStatusError as e:
            _api_error("Failed to start wallet-link flow", e)
        except httpx.RequestError as e:
            _error(f"Network error: {e}")

        link_url = pending["link_url"]
        expires_in = pending.get("expires_in", 900)

        # The audience for this stderr block is the AI agent that invoked
        # the CLI, not a human directly. Wording is aimed at the agent and
        # tells it what to DO with the URL (share with its human operator)
        # rather than describing the link as if the agent itself should click.
        # stdout stays machine-readable (final JSON) for script pipelines.
        typer.echo(
            f"\nShow this link to your human operator so they can pair a Solana\n"
            f"wallet (Phantom / Solflare / Ledger-via-Phantom / mobile) to this\n"
            f"agent. The human's private key never touches you or this host.\n"
            f"\n    {link_url}\n"
            f"\nSafe to share with the operator. Don't post it publicly — anyone\n"
            f"with the link + a Solana wallet could link THEIR wallet instead,\n"
            f"and the nonce is single-use.\n"
            f"\nLink expires in ~{int(expires_in / 60)} min. "
            f"Waiting for your human to complete the link…",
            err=True,
        )

        if no_wait:
            _output(pending)
            return

        # Poll /v1/agents/me until wallet_linked flips. Respect timeout;
        # use stderr for progress dots so stdout JSON stays clean.
        deadline = time.monotonic() + poll_timeout
        while time.monotonic() < deadline:
            try:
                me = client.auth.status(fields="agent")
            except httpx.HTTPStatusError as e:
                _api_error("Polling /v1/agents/me failed", e)
            except httpx.RequestError as e:
                # transient — don't hard-fail on a flaky read mid-poll
                typer.echo(f"  (transient read error: {e})", err=True)
                time.sleep(poll_interval)
                continue

            agent = me.get("agent") or me
            if agent.get("wallet_linked"):
                typer.echo(
                    "\n✓ Your human linked a wallet. You're now set up to validate.",
                    err=True,
                )
                _output({"wallet_address": agent.get("wallet_address"), "agent_id": agent.get("id")})
                return

            typer.echo(".", nl=False, err=True)
            time.sleep(poll_interval)

        _error(
            f"Timed out after {int(poll_timeout)}s waiting for your human operator to complete the link. "
            f"The link may still be valid (15-min TTL from creation); if your human is still working on it, "
            f"re-run `alphakek auth link-wallet --poll-timeout N` to keep polling without minting a new URL, "
            f"or re-run `alphakek auth link-wallet` to start fresh.",
            status=2,
        )
        return

    # ── Expert: --signature (external signer) ──────────────────────
    if signature:
        try:
            result = client.auth.link_wallet(wallet_address=wallet_address, signature=signature)
        except httpx.HTTPStatusError as e:
            _api_error("Failed to link wallet", e)
        except httpx.RequestError as e:
            _error(f"Network error: {e}")
        _output(result)
        return

    # ── Expert: --private-key (CLI signs) ──────────────────────────
    # Sign locally with solders then reuse the same POST as --signature.
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
