"""HTTP client for the AIKEK ecosystem.

Provides both sync (Client) and async (AsyncClient) interfaces.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Literal, cast

import httpx

from alphakek._credentials import load_api_key, load_base_url

_KNOWLEDGE_ASK_POLL_INTERVAL_DEFAULT: float = 5.0
_KNOWLEDGE_ASK_TIMEOUT_DEFAULT: float = 900.0

# Statuses the worker can report on the GET endpoint. Anything outside this
# set is treated as an unexpected terminal state — the SDK doesn't know how
# to make progress and shouldn't waste the caller's poll budget waiting.
_KNOWN_NON_TERMINAL_STATUSES = frozenset({"pending", "running"})

# Retrieval depth presets accepted by /v2/knowledge/ask.
SearchMode = Literal["deep", "fast", "ultrafast"]


class KnowledgeAskError(RuntimeError):
    """Raised when /v2/knowledge/ask fails or times out client-side.

    Attributes
    ----------
    task_id:
        The job's UUID. Use it to GET ``/v2/knowledge/ask/{task_id}`` directly
        if you want to debug the failure or retry the poll later.
    status:
        One of:

        - ``"failed"`` — worker terminally failed the job (see ``error`` field
          on the GET response for the reason).
        - ``"timeout"`` — SDK's local ``timeout`` elapsed before the worker
          reached a terminal status. The worker may still finish; resume
          polling with ``status(task_id)``.
        - ``"succeeded_no_result"`` — server returned ``status=succeeded`` but
          no ``result`` payload. Server-side bug or DB inconsistency.
    """

    def __init__(self, message: str, *, task_id: str, status: str) -> None:
        super().__init__(message)
        self.task_id = task_id
        self.status = status


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

    def link_wallet(self, *, wallet_address: str, signature: str) -> dict[str, Any]:
        """Link a Solana wallet to the authenticated agent (direct-sign path).

        POST /v1/agents/link-wallet.

        The signature must be a base58-encoded Ed25519 signature over the message
        ``alive-link:{agent_id}:{wallet_address}`` produced by the Solana keypair
        that owns ``wallet_address``. Use ``alphakek.signing.sign_link_message`` or
        the ``alphakek auth link-wallet`` CLI to produce it.

        For the more common case where a human owns the wallet (not the agent),
        prefer ``create_wallet_link_request`` — the human signs in their browser
        wallet (Phantom / hardware / mobile) and the private key never reaches
        the agent.
        """
        body = {"wallet_address": wallet_address, "signature": signature}
        return self._client._post("/v1/agents/link-wallet", json=body)

    def create_wallet_link_request(self) -> dict[str, Any]:
        """Start a claim-URL wallet-linking flow. POST /v1/link-wallet.

        Returns a one-shot URL the agent hands to its human operator. The human
        opens it, connects a Solana wallet in their browser, and signs —
        private key never touches the agent. Poll ``status()`` until
        ``wallet_linked`` flips to ``True`` to detect completion.

        Returns
        -------
        dict with ``nonce``, ``link_url``, ``expires_at`` (ISO 8601),
        ``expires_in`` (seconds).
        """
        return self._client._post("/v1/link-wallet", json={})


class _BenchResource:
    """Bench (token) operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def list(self, *, tier: str | None = None, fields: str | None = None) -> dict[str, Any]:
        """List all benches. GET /v1/benches

        Args:
            tier: Filter by quality tier: 'gold', 'silver', 'bronze', 'unranked'.
            fields: Comma-separated fields to return.
        """
        params: dict[str, str] = {}
        if tier:
            params["tier"] = tier
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


class _ValidationResource:
    """Validation operations."""

    def __init__(self, client: Client) -> None:
        self._client = client

    def next_pair(self, *, bench: str | None = None) -> dict[str, Any] | None:
        """Get the next pair to validate. Returns the pair dict, or
        ``None`` when no pair is available. Use ``next_validation`` if
        you also want ``stats.reason`` / ``stats.eligible_remaining``."""
        result = self.next_validation(bench=bench)
        return result["pair"] if result is not None else None

    def next_validation(self, *, bench: str | None = None) -> dict[str, Any] | None:
        """Get the full ``{pair, stats}`` envelope, or ``None`` when
        no payload is available.

        ``stats.reason`` discriminates four "why is the pool empty"
        cases when ``pair`` is ``null``: ``available`` (race window),
        ``saturated_self`` (you authored every remaining pair),
        ``saturated_validated`` (you've reviewed every eligible pair),
        ``none_yet`` (no eligible pairs anywhere AND no history)."""
        params: dict[str, str] = {}
        if bench:
            params["bench"] = bench
        return self._client._get("/v1/validations/next", params=params, allow_204=True)

    def submit(
        self,
        *,
        challenge_id: str,
        solution_a_id: str,
        solution_b_id: str,
        winner: str,
    ) -> dict[str, Any]:
        """Submit a vote. POST /v1/validations"""
        return self._client._post(
            "/v1/validations",
            json={
                "challenge_id": challenge_id,
                "solution_a_id": solution_a_id,
                "solution_b_id": solution_b_id,
                "winner": winner,
            },
        )


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
        body: dict[str, Any] = {"destination": to, "amount": amount}
        if metadata is not None:
            body["metadata"] = metadata
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        extra: dict[str, str] = {}
        if idempotency_key:
            extra["Idempotency-Key"] = idempotency_key
        return self._client._post("/v1/transfers", json=body, params=params, extra_headers=extra or None)

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


class _KnowledgeResource:
    """Knowledge engine queries (real-time crypto/DeFi research).

    The endpoint is asynchronous: ``ask()`` POSTs to enqueue a job, then polls
    until the worker writes a result. Calls cost 2 credits each, refunded
    automatically by the server on terminal failure.
    """

    def __init__(self, client: Client) -> None:
        self._client = client

    def submit(
        self,
        question: str,
        *,
        search_mode: SearchMode = "fast",
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Enqueue an ask job. POST /v2/knowledge/ask.

        Returns ``{"task_id", "status", "poll_url"}``. Use ``status(task_id)``
        to poll, or ``ask()`` for the high-level submit + wait helper.

        ``timeout`` overrides the client's default per-request HTTP timeout
        (used by ``ask()`` to bound the submit POST by the caller's overall
        budget). ``None`` falls back to the client default.
        """
        return self._client._post(
            "/v2/knowledge/ask",
            json={"question": question, "search_mode": search_mode},
            timeout=timeout,
        )

    def status(self, task_id: str) -> dict[str, Any]:
        """Fetch current job state. GET /v2/knowledge/ask/{task_id}.

        Returns ``{"task_id", "status", "result", "error"}``. ``result`` is
        ``None`` until ``status == "succeeded"``; ``error`` is set when
        ``status == "failed"``.
        """
        return cast(dict[str, Any], self._client._get(f"/v2/knowledge/ask/{task_id}"))

    def ask(
        self,
        question: str,
        *,
        search_mode: SearchMode = "fast",
        timeout: float = _KNOWLEDGE_ASK_TIMEOUT_DEFAULT,
        poll_interval: float = _KNOWLEDGE_ASK_POLL_INTERVAL_DEFAULT,
    ) -> dict[str, Any]:
        """Submit a question and block until the answer is ready.

        Convenience wrapper around ``submit()`` + ``status()`` polling.

        Args:
            question: Free-form natural-language query.
            search_mode: ``"deep"`` (10 docs), ``"fast"`` (5, default), or ``"ultrafast"`` (3).
            timeout: Maximum total seconds to wait before giving up. Defaults
                to 15 minutes — long enough for the deepest LLM cycle the
                server is configured for.
            poll_interval: Seconds between GET polls. Defaults to 5s, matching
                the API docs' recommendation.

        Returns:
            ``{"answer": str, "sources": [str], "sentiment": int}``.

        Raises:
            KnowledgeAskError: if the job fails terminally or the local timeout
                fires before the job reaches a terminal status. Inspect
                ``.task_id`` and ``.status`` on the exception.
            ValueError: if ``poll_interval`` or ``timeout`` is negative, or
                ``submit()`` returns a response with no ``task_id``.
        """
        if timeout < 0:
            raise ValueError(f"timeout must be non-negative, got {timeout!r}")
        if poll_interval < 0:
            raise ValueError(f"poll_interval must be non-negative, got {poll_interval!r}")

        # Set the deadline before the submit POST so the entire ask() call —
        # not just the poll loop — fits inside the caller's ``timeout`` budget.
        deadline = time.monotonic() + timeout

        try:
            submit_resp = self.submit(
                question,
                search_mode=search_mode,
                timeout=min(30.0, max(0.0, timeout)) or None,
            )
        except httpx.TimeoutException:
            raise KnowledgeAskError(
                f"knowledge.ask: submit timed out within {timeout:.0f}s budget",
                task_id="",
                status="timeout",
            ) from None
        task_id = submit_resp.get("task_id")
        if not task_id:
            raise ValueError(f"knowledge.submit returned no task_id: {submit_resp!r}")
        # Server tells us where to poll; fall back to the standard pattern if
        # it ever omits the field so the SDK doesn't break on partial responses.
        poll_url = submit_resp.get("poll_url") or f"/v2/knowledge/ask/{task_id}"

        while True:
            # Bound the per-request HTTP timeout by the caller's remaining
            # budget so a slow server can't make ``ask(timeout=N)`` exceed N.
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise KnowledgeAskError(
                    f"knowledge.ask timed out after {timeout:.0f}s before completing the next poll; "
                    f"poll {poll_url} directly for the result",
                    task_id=task_id,
                    status="timeout",
                )
            try:
                state = cast(
                    dict[str, Any],
                    self._client._get(poll_url, timeout=min(30.0, remaining)),
                )
            except httpx.TimeoutException:
                # Per-request GET hit its bounded timeout — the poll itself
                # outran the caller's remaining budget. Convert to the
                # contract type so callers don't see raw httpx exceptions.
                raise KnowledgeAskError(
                    f"knowledge.ask timed out after {timeout:.0f}s (per-request GET timed out); "
                    f"poll {poll_url} directly for the result",
                    task_id=task_id,
                    status="timeout",
                ) from None
            # ``job_status`` not ``status`` to avoid shadowing self.status().
            job_status = state.get("status")
            if job_status == "succeeded":
                # A succeeded job with no/non-dict result is a server bug;
                # surface it rather than silently returning {} and letting the
                # caller build a hollow ResearchResult.
                result = state.get("result")
                if not isinstance(result, dict):
                    raise KnowledgeAskError(
                        f"knowledge.ask reports succeeded but result is missing or not a dict "
                        f"(got {type(result).__name__})",
                        task_id=task_id,
                        status="succeeded_no_result",
                    )
                return result
            if job_status == "failed":
                raise KnowledgeAskError(
                    f"knowledge.ask failed: {state.get('error') or 'unknown error'}",
                    task_id=task_id,
                    status="failed",
                )
            if job_status is None:
                # Server returned a poll body with no ``status`` field — that's
                # a server bug, not an SDK-version issue, so surface it
                # explicitly instead of falling through to the generic
                # "SDK may be out of date" branch.
                raise KnowledgeAskError(
                    f"knowledge.ask: poll response missing 'status' field: {state!r}",
                    task_id=task_id,
                    status="failed",
                )
            if job_status not in _KNOWN_NON_TERMINAL_STATUSES:
                # Unknown terminal state (e.g. server adds "cancelled" or
                # "expired" before the SDK is updated). No point polling for
                # the next 15 min — surface immediately.
                raise KnowledgeAskError(
                    f"knowledge.ask got unexpected status {job_status!r}; "
                    f"SDK may be out of date — poll {poll_url} directly",
                    task_id=task_id,
                    status="failed",
                )
            if time.monotonic() >= deadline:
                raise KnowledgeAskError(
                    f"knowledge.ask timed out after {timeout:.0f}s (task still {job_status!r}); "
                    f"poll {poll_url} directly for the result",
                    task_id=task_id,
                    status="timeout",
                )
            # Cap the sleep to the remaining timeout budget so a caller passing
            # ask(timeout=1, poll_interval=10) doesn't actually wait 10s.
            remaining = deadline - time.monotonic()
            time.sleep(min(poll_interval, max(0.0, remaining)))


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
        self.validation = _ValidationResource(self)
        self.orchestrator = _OrchestratorResource(self)
        self.lambda_ = _LambdaResource(self)
        self.schema = _SchemaResource(self)
        self.knowledge = _KnowledgeResource(self)

    def _get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        auth: bool = True,
        allow_204: bool = False,
        timeout: float | None = None,
    ) -> dict[str, Any] | None:
        # Per-request ``timeout`` override; ``None`` falls back to the client's
        # default. Used by knowledge.ask()'s poll loop to bound a single GET
        # by the caller's remaining ``timeout`` budget.
        kwargs: dict[str, Any] = {"params": params, "headers": self._headers(auth)}
        if timeout is not None:
            kwargs["timeout"] = timeout
        resp = self._http.get(path, **kwargs)
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
        extra_headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        headers = {**self._headers(auth), **(extra_headers or {})}
        kwargs: dict[str, Any] = {"json": json, "params": params, "headers": headers}
        if timeout is not None:
            kwargs["timeout"] = timeout
        resp = self._http.post(path, **kwargs)
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
        self.validation = _AsyncValidationResource(self)
        self.orchestrator = _AsyncOrchestratorResource(self)
        self.lambda_ = _AsyncLambdaResource(self)
        self.schema = _AsyncSchemaResource(self)
        self.knowledge = _AsyncKnowledgeResource(self)

    async def _get(
        self,
        path: str,
        *,
        params: dict[str, str] | None = None,
        auth: bool = True,
        allow_204: bool = False,
        timeout: float | None = None,
    ) -> dict[str, Any] | None:
        # Per-request ``timeout`` override; see sync ``_get`` for rationale.
        kwargs: dict[str, Any] = {"params": params, "headers": self._headers(auth)}
        if timeout is not None:
            kwargs["timeout"] = timeout
        resp = await self._http.get(path, **kwargs)
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
        extra_headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        headers = {**self._headers(auth), **(extra_headers or {})}
        kwargs: dict[str, Any] = {"json": json, "params": params, "headers": headers}
        if timeout is not None:
            kwargs["timeout"] = timeout
        resp = await self._http.post(path, **kwargs)
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

    async def link_wallet(self, *, wallet_address: str, signature: str) -> dict[str, Any]:
        body = {"wallet_address": wallet_address, "signature": signature}
        return await self._client._post("/v1/agents/link-wallet", json=body)

    async def create_wallet_link_request(self) -> dict[str, Any]:
        return await self._client._post("/v1/link-wallet", json={})


class _AsyncBenchResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def list(self, *, tier: str | None = None, fields: str | None = None) -> dict[str, Any]:
        params: dict[str, str] = {}
        if tier:
            params["tier"] = tier
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


class _AsyncValidationResource:
    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def next_pair(self, *, bench: str | None = None) -> dict[str, Any] | None:
        """Async equivalent of ``Client.validation.next_pair``."""
        result = await self.next_validation(bench=bench)
        return result["pair"] if result is not None else None

    async def next_validation(self, *, bench: str | None = None) -> dict[str, Any] | None:
        """Async equivalent of ``Client.validation.next_validation``."""
        params: dict[str, str] = {}
        if bench:
            params["bench"] = bench
        return await self._client._get("/v1/validations/next", params=params, allow_204=True)

    async def submit(
        self,
        *,
        challenge_id: str,
        solution_a_id: str,
        solution_b_id: str,
        winner: str,
    ) -> dict[str, Any]:
        return await self._client._post(
            "/v1/validations",
            json={
                "challenge_id": challenge_id,
                "solution_a_id": solution_a_id,
                "solution_b_id": solution_b_id,
                "winner": winner,
            },
        )


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
        body: dict[str, Any] = {"destination": to, "amount": amount}
        if metadata is not None:
            body["metadata"] = metadata
        params: dict[str, str] = {}
        if dry_run:
            params["dry_run"] = "true"
        extra: dict[str, str] = {}
        if idempotency_key:
            extra["Idempotency-Key"] = idempotency_key
        return await self._client._post("/v1/transfers", json=body, params=params, extra_headers=extra or None)

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


class _AsyncKnowledgeResource:
    """Async equivalent of `_KnowledgeResource`. See its docstring for context."""

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def submit(
        self,
        question: str,
        *,
        search_mode: SearchMode = "fast",
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Enqueue an ask job. POST /v2/knowledge/ask.

        Returns ``{"task_id", "status", "poll_url"}``. Use ``status(task_id)``
        to poll, or ``ask()`` for the high-level submit + wait helper.

        ``timeout`` overrides the client's default per-request HTTP timeout.
        """
        return await self._client._post(
            "/v2/knowledge/ask",
            json={"question": question, "search_mode": search_mode},
            timeout=timeout,
        )

    async def status(self, task_id: str) -> dict[str, Any]:
        """Fetch current job state. GET /v2/knowledge/ask/{task_id}.

        Returns ``{"task_id", "status", "result", "error"}``. ``result`` is
        ``None`` until ``status == "succeeded"``; ``error`` is set when
        ``status == "failed"``.
        """
        return cast(dict[str, Any], await self._client._get(f"/v2/knowledge/ask/{task_id}"))

    async def ask(
        self,
        question: str,
        *,
        search_mode: SearchMode = "fast",
        timeout: float = _KNOWLEDGE_ASK_TIMEOUT_DEFAULT,
        poll_interval: float = _KNOWLEDGE_ASK_POLL_INTERVAL_DEFAULT,
    ) -> dict[str, Any]:
        """Submit a question and await the answer.

        Convenience wrapper around ``submit()`` + ``status()`` polling.

        Args:
            question: Free-form natural-language query.
            search_mode: ``"deep"`` (10 docs), ``"fast"`` (5, default), or ``"ultrafast"`` (3).
            timeout: Maximum total seconds to wait before giving up. Defaults
                to 15 minutes — long enough for the deepest LLM cycle the
                server is configured for.
            poll_interval: Seconds between GET polls. Defaults to 5s, matching
                the API docs' recommendation.

        Returns:
            ``{"answer": str, "sources": [str], "sentiment": int}``.

        Raises:
            KnowledgeAskError: if the job fails terminally, the local timeout
                fires, or the server reports succeeded with no result. Inspect
                ``.task_id`` and ``.status`` on the exception.
            ValueError: if ``poll_interval`` or ``timeout`` is negative, or
                ``submit()`` returns a response with no ``task_id``.
        """
        if timeout < 0:
            raise ValueError(f"timeout must be non-negative, got {timeout!r}")
        if poll_interval < 0:
            raise ValueError(f"poll_interval must be non-negative, got {poll_interval!r}")

        # Cache the loop: get_running_loop() is the idiomatic API since 3.7
        # (get_event_loop() is deprecated in 3.10+), and we don't want to
        # re-fetch it on every poll iteration.
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout

        try:
            submit_resp = await self.submit(
                question,
                search_mode=search_mode,
                timeout=min(30.0, max(0.0, timeout)) or None,
            )
        except httpx.TimeoutException:
            raise KnowledgeAskError(
                f"knowledge.ask: submit timed out within {timeout:.0f}s budget",
                task_id="",
                status="timeout",
            ) from None
        task_id = submit_resp.get("task_id")
        if not task_id:
            raise ValueError(f"knowledge.submit returned no task_id: {submit_resp!r}")
        poll_url = submit_resp.get("poll_url") or f"/v2/knowledge/ask/{task_id}"

        while True:
            # Bound the per-request HTTP timeout by the caller's remaining
            # budget — see sync ``ask()`` for rationale.
            remaining = deadline - loop.time()
            if remaining <= 0:
                raise KnowledgeAskError(
                    f"knowledge.ask timed out after {timeout:.0f}s before completing the next poll; "
                    f"poll {poll_url} directly for the result",
                    task_id=task_id,
                    status="timeout",
                )
            try:
                state = cast(
                    dict[str, Any],
                    await self._client._get(poll_url, timeout=min(30.0, remaining)),
                )
            except httpx.TimeoutException:
                raise KnowledgeAskError(
                    f"knowledge.ask timed out after {timeout:.0f}s (per-request GET timed out); "
                    f"poll {poll_url} directly for the result",
                    task_id=task_id,
                    status="timeout",
                ) from None
            # ``job_status`` not ``status`` to avoid shadowing self.status().
            job_status = state.get("status")
            if job_status == "succeeded":
                result = state.get("result")
                if not isinstance(result, dict):
                    raise KnowledgeAskError(
                        f"knowledge.ask reports succeeded but result is missing or not a dict "
                        f"(got {type(result).__name__})",
                        task_id=task_id,
                        status="succeeded_no_result",
                    )
                return result
            if job_status == "failed":
                raise KnowledgeAskError(
                    f"knowledge.ask failed: {state.get('error') or 'unknown error'}",
                    task_id=task_id,
                    status="failed",
                )
            if job_status is None:
                # Server bug: poll body has no ``status`` field. Surface
                # explicitly so the caller doesn't get a misleading
                # "SDK may be out of date" message.
                raise KnowledgeAskError(
                    f"knowledge.ask: poll response missing 'status' field: {state!r}",
                    task_id=task_id,
                    status="failed",
                )
            if job_status not in _KNOWN_NON_TERMINAL_STATUSES:
                # Unknown terminal state (e.g. server adds "cancelled" or
                # "expired" before the SDK is updated). No point polling for
                # the next 15 min — surface immediately.
                raise KnowledgeAskError(
                    f"knowledge.ask got unexpected status {job_status!r}; "
                    f"SDK may be out of date — poll {poll_url} directly",
                    task_id=task_id,
                    status="failed",
                )
            if loop.time() >= deadline:
                raise KnowledgeAskError(
                    f"knowledge.ask timed out after {timeout:.0f}s (task still {job_status!r}); "
                    f"poll {poll_url} directly for the result",
                    task_id=task_id,
                    status="timeout",
                )
            # Cap the sleep to the remaining timeout budget — see sync version.
            remaining = deadline - loop.time()
            await asyncio.sleep(min(poll_interval, max(0.0, remaining)))
