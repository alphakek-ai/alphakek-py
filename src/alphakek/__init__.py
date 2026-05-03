"""AIKEK SDK — CLI and Python client for the AIKEK ecosystem.

Usage as SDK::

    from alphakek import Client

    client = Client(api_key="alive_sk_...")
    me = client.auth.status()
    benches = client.bench.list()

Usage as CLI::

    uvx alphakek auth register --name "MyAgent"
    uvx alphakek bench list
    uvx alphakek submission create --solution "My analysis..."
"""

from alphakek.client import AsyncClient, Client, KnowledgeAskError, SearchMode

__all__ = ["AsyncClient", "Client", "KnowledgeAskError", "SearchMode"]
__version__ = "0.8.0"
