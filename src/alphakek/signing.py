"""Solana signing helpers for operations that require a wallet signature.

Kept isolated so the rest of the SDK doesn't depend on ``solders``. Install with
``pip install 'alphakek[solana]'`` to enable.
"""

from __future__ import annotations

import json
from pathlib import Path

try:
    from solders.keypair import Keypair
except ImportError as e:
    raise ImportError(
        "alphakek's wallet-linking feature requires the optional 'solders' dependency "
        "(Solana Ed25519 signing). Install it with one of:\n"
        "  pip install 'alphakek[solana]'\n"
        "  uv pip install 'alphakek[solana]'\n"
        "  uvx --with solders alphakek auth link-wallet ...\n"
        "Then rerun the command. No other alphakek commands need this."
    ) from e


def load_keypair(key: str) -> Keypair:
    """Load a Solana keypair from any of: base58 secret, JSON byte array, or path to a ``.json`` keyfile.

    Solana CLI keyfiles (``~/.config/solana/id.json``) store a 64-byte array.
    Phantom/phrases commonly export the full 64-byte secret as a base58 string.
    Both are accepted.
    """
    key = key.strip()

    if key.startswith("[") and key.endswith("]"):
        return Keypair.from_bytes(bytes(json.loads(key)))

    path = Path(key).expanduser()
    if path.is_file():
        return Keypair.from_bytes(bytes(json.loads(path.read_text())))

    return Keypair.from_base58_string(key)


def sign_link_message(keypair: Keypair, agent_id: str) -> tuple[str, str]:
    """Sign the ``alive-link`` message; returns ``(wallet_address, signature_base58)``."""
    wallet_address = str(keypair.pubkey())
    message = f"alive-link:{agent_id}:{wallet_address}".encode()
    signature = keypair.sign_message(message)
    return wallet_address, str(signature)
