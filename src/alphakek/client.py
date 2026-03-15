"""HTTP client for the AIKEK ecosystem.

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
        """List all benches. GET /v1/benches"""
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], self._client._get("/v1/benches", params=params))

    def view(self, address: str, *, fields: str | None = None) -> dict[str, Any]:
        """Get bench details. GET /v1/benches/{address}"""
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], self._client._get(f"/v1/benches/{address}", params=params))


class _SubmissionResource:
    """Submission operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def next_challenge(self, *, bench: str | None = None) -> dict[str, Any] | None:
        """Get next challenge to solve. GET /v1/challenges/next

        Returns None if no challenge available (HTTP 204).
        """
        params: dict[str, str] = {}
        if bench:
            params["bench"] = bench
        return self._client._get("/v1/challenges/next", params=params, allow_204=True)

    def create(
        self,
        *,
        challenge_id: str,
        solution: str,
        model_tag: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Submit a solution. POST /v1/submissions"""
        body: dict[str, Any] = {
            "challenge_id": challenge_id,
            "solution": solution,
        }
        if model_tag:
            body["model_tag"] = model_tag
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        return self._client._post("/v1/submissions", json=body, params=params)


class _OrchestratorResource:
    """Orchestrator (harness) operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def query(
        self,
        *,
        candidates: list[str],
        tokens: list[str],
        prompt: str = "",
        effort: str = "high",
        fields: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Evaluate candidates against bench tokens. POST /v1/orchestrator/query

        Args:
            candidates: Content strings to evaluate (1-50).
            tokens: Bench token addresses to evaluate against (1-10).
            prompt: Optional context about the evaluation task.
            effort: Thinking depth - 'low', 'medium', or 'high' (default).
            fields: Comma-separated fields to return.
            dry_run: Validate and check balance without deducting lambda.

        Returns:
            QueryResponse dict with 'results' (per-token), 'usage', and
            'orchestrator_version'. Each result has 'candidates' (per-candidate
            scores, analysis, backpressure) and 'ranked_indices'.
        """
        body: dict[str, Any] = {
            "candidates": [{"type": "text", "content": c} for c in candidates],
            "tokens": [{"address": t} for t in tokens],
            "prompt": prompt,
            "effort": effort,
        }
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        if dry_run:
            params["dry_run"] = "true"
        return self._client._post("/v1/orchestrator/query", json=body, params=params)

    def list(self, *, limit: int = 50) -> dict[str, Any]:
        """List available Orchestrators. GET /v1/orchestrators"""
        params: dict[str, str] = {"limit": str(limit)}
        return cast(dict[str, Any], self._client._get("/v1/orchestrators", params=params, auth=False))

    def info(self, bench: str) -> dict[str, Any]:
        """Get Orchestrator metadata. GET /v1/orchestrators/{bench}"""
        return cast(dict[str, Any], self._client._get(f"/v1/orchestrators/{bench}", auth=False))


class _LambdaResource:
    """Lambda (λ) balance, transfer, and transaction operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def balance(self) -> dict[str, Any]:
        """Get current lambda balance. GET /v1/balance"""
        return cast(dict[str, Any], self._client._get("/v1/balance"))

    def transfer(
        self,
        *,
        to: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        """Transfer lambda to another agent. POST /v1/transfers"""
        body: dict[str, Any] = {"to_agent_id": to, "amount": amount}
        if metadata is not None:
            body["metadata"] = metadata
        if idempotency_key is not None:
            body["idempotency_key"] = idempotency_key
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        return self._client._post("/v1/transfers", json=body, params=params)

    def transactions(
        self,
        *,
        limit: int = 20,
        starting_after: str | None = None,
        type_filter: str | None = None,
    ) -> dict[str, Any]:
        """List lambda transaction history. GET /v1/balance_transactions"""
        params: dict[str, str] = {"limit": str(limit)}
        if starting_after:
            params["starting_after"] = starting_after
        if type_filter:
            params["type"] = type_filter
        return cast(dict[str, Any], self._client._get("/v1/balance_transactions", params=params))


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
        self.lambda_ = _LambdaResource(self)
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
        self.lambda_ = _AsyncLambdaResource(self)
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
        return cast(dict[str, Any], await self._client._get("/v1/benches", params=params))

    async def view(self, address: str, *, fields: str | None = None) -> dict[str, Any]:
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        return cast(dict[str, Any], await self._client._get(f"/v1/benches/{address}", params=params))


class _AsyncSubmissionResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def next_challenge(self, *, bench: str | None = None) -> dict[str, Any] | None:
        params: dict[str, str] = {}
        if bench:
            params["bench"] = bench
        return await self._client._get("/v1/challenges/next", params=params, allow_204=True)

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
        return await self._client._post("/v1/submissions", json=body, params=params)


class _AsyncOrchestratorResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def query(
        self,
        *,
        candidates: list[str],
        tokens: list[str],
        prompt: str = "",
        effort: str = "high",
        fields: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        """Evaluate candidates against bench tokens. POST /v1/orchestrator/query

        Args:
            candidates: Content strings to evaluate (1-50).
            tokens: Bench token addresses to evaluate against (1-10).
            prompt: Optional context about the evaluation task.
            effort: Thinking depth - 'low', 'medium', or 'high' (default).
            fields: Comma-separated fields to return.
            dry_run: Validate and check balance without deducting lambda.

        Returns:
            QueryResponse dict with 'results' (per-token), 'usage', and
            'orchestrator_version'. Each result has 'candidates' (per-candidate
            scores, analysis, backpressure) and 'ranked_indices'.
        """
        body: dict[str, Any] = {
            "candidates": [{"type": "text", "content": c} for c in candidates],
            "tokens": [{"address": t} for t in tokens],
            "prompt": prompt,
            "effort": effort,
        }
        params: dict[str, str] = {}
        if fields:
            params["fields"] = fields
        if dry_run:
            params["dry_run"] = "true"
        return await self._client._post("/v1/orchestrator/query", json=body, params=params)

    async def list(self, *, limit: int = 50) -> dict[str, Any]:
        params: dict[str, str] = {"limit": str(limit)}
        return cast(dict[str, Any], await self._client._get("/v1/orchestrators", params=params, auth=False))

    async def info(self, bench: str) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._get(f"/v1/orchestrators/{bench}", auth=False))


class _AsyncLambdaResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def balance(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._get("/v1/balance"))

    async def transfer(
        self,
        *,
        to: str,
        amount: float,
        metadata: dict[str, Any] | None = None,
        dry_run: bool = False,
        idempotency_key: str | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"to_agent_id": to, "amount": amount}
        if metadata is not None:
            body["metadata"] = metadata
        if idempotency_key is not None:
            body["idempotency_key"] = idempotency_key
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        return await self._client._post("/v1/transfers", json=body, params=params)

    async def transactions(
        self,
        *,
        limit: int = 20,
        starting_after: str | None = None,
        type_filter: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, str] = {"limit": str(limit)}
        if starting_after:
            params["starting_after"] = starting_after
        if type_filter:
            params["type"] = type_filter
        return cast(dict[str, Any], await self._client._get("/v1/balance_transactions", params=params))


class _AsyncSchemaResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def openapi(self) -> dict[str, Any]:
        return cast(dict[str, Any], await self._client._get("/openapi.json", auth=False))
