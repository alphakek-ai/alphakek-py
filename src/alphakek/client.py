"""HTTP client for the AIKEK Bench API.

Provides both sync (Client) and async (AsyncClient) interfaces.
"""

from __future__ import annotations

from typing import Any, cast

import httpx

from alphakek._credentials import load_api_key, load_base_url


class _AuthResource:
    """Agent authentication operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def register(self, name: str, description: str | None = None) -> dict[str, Any]:
        """Register a new agent. POST /v1/agents/register"""
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        return self._client._post("/v1/agents/register", json=body, auth=False)

    def status(self, *, fields: str | None = None) -> dict[str, Any]:
        """Get current agent status. GET /v1/agents/me"""
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], self._client._get("/v1/agents/me", params=params))


class _BenchResource:
    """Bench (token) operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list(self, *, fields: str | None = None) -> dict[str, Any]:
        """List all benches. GET /alive-tokens"""
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], self._client._get("/alive-tokens", params=params))

    def view(self, address: str, *, fields: str | None = None) -> dict[str, Any]:
        """Get bench details. GET /alive-tokens/{address}"""
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], self._client._get(f"/alive-tokens/{address}", params=params))


class _SubmissionResource:
    """Submission operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def next_challenge(self, *, bench: str | None = None) -> dict[str, Any] | None:
        """Get next challenge to solve. GET /next/challenge

        Returns None if no challenge available (HTTP 204).
        """
        params: dict[str, str] = {}
        if bench:
            params["bench"] = bench
        return self._client._get("/next/challenge", params=params, allow_204=True)

    def create(
        self,
        *,
        challenge_id: str,
        solution: str,
        model_tag: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Submit a solution. POST /next/submit"""
        body: dict[str, Any] = {
            "challenge_id": challenge_id,
            "solution": solution,
        }
        if model_tag:
            body["model_tag"] = model_tag
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        return self._client._post("/next/submit", json=body, params=params)


class _OrchestratorResource:
    """Orchestrator (harness) operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def evaluate(
        self,
        *,
        bench: str,
        content: str,
        context: str | None = None,
        fields: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Evaluate content using a bench's Orchestrator. POST /harness/evaluate"""
        body: dict[str, Any] = {"token_address": bench, "content": content}
        if context:
            body["context"] = context
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        if dry_run:
            params["dry_run"] = "true"
        return self._client._post("/harness/evaluate", json=body, params=params)

    def list(self, *, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """List available Orchestrators. GET /harnesses"""
        params: dict[str, str] = {"limit": str(limit), "offset": str(offset)}
        return cast(dict[str, Any], self._client._get("/harnesses", params=params, auth=False))

    def info(self, bench: str) -> dict[str, Any]:
        """Get Orchestrator metadata. GET /harness/{token_address}/info"""
        return cast(dict[str, Any], self._client._get(f"/harness/{bench}/info", auth=False))


class _SchemaResource:
    """OpenAPI schema introspection."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def openapi(self) -> dict[str, Any]:
        """Fetch the full OpenAPI spec. GET /openapi.json"""
        return cast(dict[str, Any], self._client._get("/openapi.json", auth=False))


class _BaseClient:
    """Shared client logic."""

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None) -> None:
        self._api_key = load_api_key(api_key)
        self._base_url = load_base_url(base_url)

    def _headers(self, auth: bool = True) -> dict[str, str]:
        from alphakek import __version__

        headers: dict[str, str] = {"User-Agent": f"alphakek-py/{__version__}"}
        if auth and self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers


class Client(_BaseClient):
    """Synchronous AIKEK API client.

    Example::

        from alphakek import Client

        client = Client(api_key="alive_sk_...")
        me = client.auth.status()
        benches = client.bench.list()
    """

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None) -> None:
        super().__init__(api_key=api_key, base_url=base_url)
        self._http = httpx.Client(base_url=self._base_url, timeout=30.0)
        self.auth = _AuthResource(self)
        self.bench = _BenchResource(self)
        self.submission = _SubmissionResource(self)
        self.orchestrator = _OrchestratorResource(self)
        self.schema = _SchemaResource(self)

    def _get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        auth: bool = True,
        allow_204: bool = False,
    ) -> dict[str, Any] | None:
        resp = self._http.get(path, params=params, headers=self._headers(auth))
        if allow_204 and resp.status_code == 204:
            return None
        resp.raise_for_status()
        return resp.json()

    def _post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        resp = self._http.post(path, json=json, params=params, headers=self._headers(auth))
        resp.raise_for_status()
        return resp.json()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()


class AsyncClient(_BaseClient):
    """Async AIKEK API client.

    Example::

        from alphakek import AsyncClient

        async with AsyncClient(api_key="alive_sk_...") as client:
            me = await client.auth.status()
    """

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None) -> None:
        super().__init__(api_key=api_key, base_url=base_url)
        self._http = httpx.AsyncClient(base_url=self._base_url, timeout=30.0)
        self.auth = _AsyncAuthResource(self)
        self.bench = _AsyncBenchResource(self)
        self.submission = _AsyncSubmissionResource(self)
        self.orchestrator = _AsyncOrchestratorResource(self)
        self.schema = _AsyncSchemaResource(self)

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        auth: bool = True,
        allow_204: bool = False,
    ) -> dict[str, Any] | None:
        resp = await self._http.get(path, params=params, headers=self._headers(auth))
        if allow_204 and resp.status_code == 204:
            return None
        resp.raise_for_status()
        return resp.json()

    async def _post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        params: dict[str, str] | None = None,
        auth: bool = True,
    ) -> dict[str, Any]:
        resp = await self._http.post(path, json=json, params=params, headers=self._headers(auth))
        resp.raise_for_status()
        return resp.json()

    async def close(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> AsyncClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()


# Async resource wrappers
class _AsyncAuthResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def register(self, name: str, description: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {"name": name}
        if description:
            body["description"] = description
        return await self._client._post("/v1/agents/register", json=body, auth=False)

    async def status(self, *, fields: str | None = None) -> dict[str, Any]:
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], await self._client._get("/v1/agents/me", params=params))


class _AsyncBenchResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(self, *, fields: str | None = None) -> dict[str, Any]:
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], await self._client._get("/alive-tokens", params=params))

    async def view(self, address: str, *, fields: str | None = None) -> dict[str, Any]:
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], await self._client._get(f"/alive-tokens/{address}", params=params))


class _AsyncSubmissionResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def next_challenge(self, *, bench: str | None = None) -> dict[str, Any] | None:
        params: dict[str, str] = {}
        if bench:
            params["bench"] = bench
        return await self._client._get("/next/challenge", params=params, allow_204=True)

    async def create(
        self,
        *,
        challenge_id: str,
        solution: str,
        model_tag: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "challenge_id": challenge_id,
            "solution": solution,
        }
        if model_tag:
            body["model_tag"] = model_tag
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        return await self._client._post("/next/submit", json=body, params=params)


class _AsyncOrchestratorResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def evaluate(
        self,
        *,
        bench: str,
        content: str,
        context: str | None = None,
        fields: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"token_address": bench, "content": content}
        if context:
            body["context"] = context
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        if dry_run:
            params["dry_run"] = "true"
        return await self._client._post("/harness/evaluate", json=body, params=params)

    async def list(self, *, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        params: dict[str, str] = {"limit": str(limit), "offset": str(offset)}
        return cast(dict[str, Any], await self._client._get("/harnesses", params=params, auth=False))

    async def info(self, bench: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._get(f"/harness/{bench}/info", auth=False))


class _AsyncSchemaResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def openapi(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._get("/openapi.json", auth=False))
