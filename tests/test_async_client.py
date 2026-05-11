"""Tests for AsyncClient using respx."""

import httpx
import pytest
import respx

from alphakek.client import AsyncClient

BASE = "https://alive-api.alphakek.ai"


@pytest.fixture
async def client():
    c = AsyncClient(api_key="alive_sk_test", base_url=BASE)
    yield c
    await c.close()


class TestAsyncAuthResource:
    @respx.mock
    async def test_register(self, client):
        respx.post(f"{BASE}/v1/agents/register").mock(
            return_value=httpx.Response(200, json={"agent_id": "abc", "api_key": "alive_sk_new"})
        )
        result = await client.auth.register(name="TestAgent")
        assert result["agent_id"] == "abc"

    @respx.mock
    async def test_status(self, client):
        respx.get(f"{BASE}/v1/agents/me").mock(
            return_value=httpx.Response(200, json={"id": "abc", "status": "claimed", "lp_balance": 42.0})
        )
        result = await client.auth.status()
        assert result["status"] == "claimed"

    @respx.mock
    async def test_status_with_fields(self, client):
        respx.get(f"{BASE}/v1/agents/me").mock(return_value=httpx.Response(200, json={"status": "claimed"}))
        result = await client.auth.status(fields="status")
        assert result["status"] == "claimed"


class TestAsyncBenchResource:
    @respx.mock
    async def test_list(self, client):
        respx.get(f"{BASE}/v1/benches").mock(
            return_value=httpx.Response(200, json={"data": [{"name": "Bench A"}], "has_more": False})
        )
        result = await client.bench.list()
        assert result["has_more"] is False

    @respx.mock
    async def test_view(self, client):
        addr = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
        respx.get(f"{BASE}/v1/benches/{addr}").mock(
            return_value=httpx.Response(200, json={"name": "Bench A", "token_address": addr})
        )
        result = await client.bench.view(addr)
        assert result["name"] == "Bench A"


class TestAsyncSubmissionResource:
    @respx.mock
    async def test_next_challenge(self, client):
        respx.get(f"{BASE}/v1/challenges/next").mock(
            return_value=httpx.Response(200, json={"id": "ch-1", "title": "Test"})
        )
        result = await client.submission.next_challenge()
        assert result["id"] == "ch-1"

    @respx.mock
    async def test_next_challenge_returns_none_on_204(self, client):
        respx.get(f"{BASE}/v1/challenges/next").mock(return_value=httpx.Response(204))
        result = await client.submission.next_challenge()
        assert result is None

    @respx.mock
    async def test_create_submission(self, client):
        respx.post(f"{BASE}/v1/submissions").mock(
            return_value=httpx.Response(200, json={"submission_id": "sub-1", "version": 1})
        )
        result = await client.submission.create(challenge_id="ch-1", solution="My analysis")
        assert result["submission_id"] == "sub-1"


class TestAsyncOrchestratorResource:
    @respx.mock
    async def test_query(self, client):
        respx.post(f"{BASE}/v1/orchestrator/query").mock(
            return_value=httpx.Response(
                200, json={"results": [], "usage": {"lambda_cost": 0.1, "lambda_remaining": 99.9}}
            )
        )
        result = await client.orchestrator.query(candidates=["Test"], tokens=["7xKXtg"])
        assert "usage" in result

    @respx.mock
    async def test_list(self, client):
        respx.get(f"{BASE}/v1/orchestrators").mock(
            return_value=httpx.Response(200, json={"data": [], "has_more": False})
        )
        result = await client.orchestrator.list()
        assert result["has_more"] is False

    @respx.mock
    async def test_info(self, client):
        respx.get(f"{BASE}/v1/orchestrators/7xKXtg").mock(
            return_value=httpx.Response(200, json={"token_name": "Pizza", "version": 3, "status": "trained"})
        )
        result = await client.orchestrator.info("7xKXtg")
        assert result["status"] == "trained"


class TestAsyncSchemaResource:
    @respx.mock
    async def test_openapi(self, client):
        respx.get(f"{BASE}/openapi.json").mock(return_value=httpx.Response(200, json={"openapi": "3.1.0", "paths": {}}))
        result = await client.schema.openapi()
        assert result["openapi"] == "3.1.0"


class TestAsyncKnowledgeResource:
    @respx.mock
    async def test_submit(self, client):
        import json

        task_id = "11111111-2222-3333-4444-555555555555"
        route = respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        result = await client.knowledge.submit("What is BTC?")
        assert result["task_id"] == task_id
        # Assert the body actually went over the wire (mirrors sync test).
        body = json.loads(route.calls[0].request.content)
        assert body == {"question": "What is BTC?", "search_mode": "fast"}

    @respx.mock
    async def test_status_returns_state(self, client):
        task_id = "11111111-2222-3333-4444-555555555555"
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "pending", "result": None})
        )
        result = await client.knowledge.status(task_id)
        assert result["status"] == "pending"

    @respx.mock
    async def test_ask_polls_until_succeeded(self, client):
        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        get_route = respx.get(f"{BASE}/v2/knowledge/ask/{task_id}")
        get_route.side_effect = [
            httpx.Response(200, json={"task_id": task_id, "status": "running", "result": None}),
            httpx.Response(
                200,
                json={
                    "task_id": task_id,
                    "status": "succeeded",
                    "result": {"answer": "BTC.", "sources": ["https://x"], "sentiment": 7},
                },
            ),
        ]
        result = await client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert result == {"answer": "BTC.", "sources": ["https://x"], "sentiment": 7}

    @respx.mock
    async def test_ask_raises_on_failure(self, client):
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(
                200,
                json={"task_id": task_id, "status": "failed", "result": None, "error": "LLM timeout"},
            )
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert exc_info.value.status == "failed"

    @respx.mock
    async def test_ask_raises_on_timeout(self, client):
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        # Always returns running — caller's local timeout should fire.
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "running", "result": None})
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", timeout=0.0, poll_interval=0.0)
        assert exc_info.value.status == "timeout"
        assert exc_info.value.task_id == task_id

    @respx.mock
    async def test_ask_raises_on_succeeded_with_no_result(self, client):
        """Server bug: status=succeeded but result missing must surface, not hide."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "succeeded", "result": None})
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert exc_info.value.status == "succeeded_no_result"

    @respx.mock
    async def test_ask_raises_on_submit_with_no_task_id(self, client):
        """Defensive: server returns an unexpected shape (no task_id key) →
        raise a typed ValueError with the response body in it instead of a
        bare KeyError. Async path runs through ``await self.submit(...)``, so
        it deserves its own coverage."""
        respx.post(f"{BASE}/v2/knowledge/ask").mock(return_value=httpx.Response(202, json={"unexpected": "shape"}))
        with pytest.raises(ValueError, match="no task_id"):
            await client.knowledge.ask("What is BTC?", poll_interval=0.0)

    async def test_ask_rejects_negative_poll_interval(self, client):
        with pytest.raises(ValueError, match="poll_interval must be non-negative"):
            await client.knowledge.ask("What is BTC?", poll_interval=-1.0)

    async def test_ask_rejects_negative_timeout(self, client):
        with pytest.raises(ValueError, match="timeout must be non-negative"):
            await client.knowledge.ask("What is BTC?", timeout=-1.0)

    @respx.mock
    async def test_ask_raises_on_missing_status_field(self, client):
        """Server bug: poll body without ``status`` must raise a 'missing status'
        error rather than the misleading 'SDK may be out of date' branch."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id})
        )
        with pytest.raises(KnowledgeAskError, match="missing 'status' field"):
            await client.knowledge.ask("What is BTC?", poll_interval=0.0)

    @respx.mock
    async def test_ask_caps_per_request_timeout_to_remaining(self, client):
        """Async mirror of the sync test: each poll GET must use a timeout no
        larger than the caller's remaining budget."""
        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        get_route = respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task_id": task_id,
                    "status": "succeeded",
                    "result": {"answer": "ok", "sources": [], "sentiment": 5},
                },
            )
        )
        await client.knowledge.ask("What is BTC?", timeout=2.0, poll_interval=0.0)
        recorded_timeout = get_route.calls[0].request.extensions.get("timeout", {})
        read_timeout = recorded_timeout.get("read") if isinstance(recorded_timeout, dict) else None
        assert read_timeout is not None and read_timeout <= 2.0, (
            f"per-request read timeout was {read_timeout!r}, expected ≤ 2s"
        )

    @respx.mock
    async def test_ask_converts_get_timeout_to_knowledge_ask_error(self, client):
        """If httpx raises TimeoutException on a poll GET, ask() must convert
        it to KnowledgeAskError(status='timeout') instead of leaking the raw
        exception (the docstring contract is KnowledgeAskError | ValueError)."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(side_effect=httpx.ReadTimeout("slow"))
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", timeout=2.0, poll_interval=0.0)
        assert exc_info.value.status == "timeout"
        assert exc_info.value.task_id == task_id

    @respx.mock
    async def test_ask_converts_submit_timeout_to_knowledge_ask_error(self, client):
        """Submit POST timing out must surface as KnowledgeAskError, not raw httpx."""
        from alphakek import KnowledgeAskError

        respx.post(f"{BASE}/v2/knowledge/ask").mock(side_effect=httpx.ConnectTimeout("slow"))
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", timeout=1.0, poll_interval=0.0)
        assert exc_info.value.status == "timeout"
        # No task created yet — task_id is empty.
        assert exc_info.value.task_id == ""

    @respx.mock
    async def test_ask_caps_poll_sleep_to_remaining_timeout(self, client):
        import asyncio as _asyncio

        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "running", "result": None})
        )

        loop = _asyncio.get_running_loop()
        start = loop.time()
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", timeout=0.1, poll_interval=5.0)
        elapsed = loop.time() - start
        assert exc_info.value.status == "timeout"
        assert elapsed < 1.0, f"ask() ignored timeout cap: {elapsed:.2f}s"

    @respx.mock
    async def test_ask_raises_on_unknown_status(self, client):
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{BASE}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{BASE}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "expired", "result": None})
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            await client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert "unexpected status 'expired'" in str(exc_info.value)


class TestAsyncValidationResource:
    """Async equivalent of the sync TestValidationResource — covers
    the new ``{pair, stats}`` shape from backend PR #366."""

    @respx.mock
    async def test_next_pair_unwraps_response_pair(self, client: AsyncClient):
        respx.get(f"{BASE}/v1/validations/next").mock(
            return_value=httpx.Response(
                200,
                json={
                    "pair": {
                        "challenge_id": "c1",
                        "solution_a_id": "sa",
                        "solution_b_id": "sb",
                        "challenge_title": "T",
                        "challenge_description": "D",
                        "solution_a_text": "A",
                        "solution_b_text": "B",
                        "token_address": "TOK",
                        "token_name": "Tok",
                        "token_symbol": "TOK",
                        "token_conviction": "C",
                    },
                    "stats": {"verified": 1, "eligible_remaining": 5, "reason": "available"},
                },
            )
        )
        result = await client.validation.next_pair()
        assert result is not None
        assert result["challenge_id"] == "c1"
        assert "stats" not in result

    @respx.mock
    async def test_next_pair_returns_none_when_pool_empty(self, client: AsyncClient):
        respx.get(f"{BASE}/v1/validations/next").mock(
            return_value=httpx.Response(
                200,
                json={
                    "pair": None,
                    "stats": {"verified": 42, "eligible_remaining": 0, "reason": "saturated_validated"},
                },
            )
        )
        assert await client.validation.next_pair() is None

    @respx.mock
    async def test_next_validation_returns_full_envelope(self, client: AsyncClient):
        respx.get(f"{BASE}/v1/validations/next").mock(
            return_value=httpx.Response(
                200,
                json={
                    "pair": None,
                    "stats": {"verified": 0, "eligible_remaining": 0, "reason": "none_yet"},
                },
            )
        )
        result = await client.validation.next_validation()
        assert result is not None
        assert result["pair"] is None
        assert result["stats"]["reason"] == "none_yet"

    @respx.mock
    async def test_next_pair_handles_legacy_204(self, client: AsyncClient):
        respx.get(f"{BASE}/v1/validations/next").mock(return_value=httpx.Response(204))
        assert await client.validation.next_pair() is None
        assert await client.validation.next_validation() is None

    @respx.mock
    async def test_next_pair_passes_bench_filter(self, client: AsyncClient):
        route = respx.get(f"{BASE}/v1/validations/next").mock(
            return_value=httpx.Response(
                200, json={"pair": None, "stats": {"verified": 0, "eligible_remaining": 0, "reason": "none_yet"}}
            )
        )
        await client.validation.next_pair(bench="9" * 32)
        assert route.called
        assert "bench=" in str(route.calls[0].request.url)


class TestAsyncContextManager:
    @respx.mock
    async def test_async_with_statement(self):
        respx.get(f"{BASE}/v1/agents/me").mock(return_value=httpx.Response(200, json={"status": "claimed"}))
        async with AsyncClient(api_key="alive_sk_test", base_url=BASE) as client:
            result = await client.auth.status()
            assert result["status"] == "claimed"

    @respx.mock
    async def test_headers_include_auth(self):
        route = respx.get(f"{BASE}/v1/agents/me").mock(return_value=httpx.Response(200, json={}))
        async with AsyncClient(api_key="alive_sk_test", base_url=BASE) as client:
            await client.auth.status()
        assert route.calls[0].request.headers["authorization"] == "Bearer alive_sk_test"
        assert "alphakek-py/" in route.calls[0].request.headers["user-agent"]
