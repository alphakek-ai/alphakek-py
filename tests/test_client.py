"""Tests for the SDK client."""

import httpx
import pytest
import respx

from alphakek.client import Client


@pytest.fixture
def base_url():
    return "https://test-api.example.com"


@pytest.fixture
def client(base_url: str):
    c = Client(api_key="alive_sk_test", base_url=base_url)
    yield c
    c.close()


class TestAuthResource:
    @respx.mock
    def test_register(self, client: Client, base_url: str):
        respx.post(f"{base_url}/v1/agents/register").mock(
            return_value=httpx.Response(
                200,
                json={
                    "agent_id": "abc-123",
                    "api_key": "alive_sk_new",
                    "verification_code": "ALIVE-XYZ",
                    "claim_url": "https://alive.alphakek.ai/claim/ALIVE-XYZ",
                    "next_steps": "Send claim_url to your human.",
                },
            )
        )
        result = client.auth.register(name="TestAgent", description="A test")
        assert result["agent_id"] == "abc-123"
        assert result["api_key"] == "alive_sk_new"

    @respx.mock
    def test_status(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/agents/me").mock(
            return_value=httpx.Response(
                200,
                json={"id": "abc-123", "name": "TestAgent", "status": "claimed", "lp_balance": 42.0},
            )
        )
        result = client.auth.status()
        assert result["status"] == "claimed"
        assert result["lp_balance"] == 42.0

    @respx.mock
    def test_status_with_fields(self, client: Client, base_url: str):
        route = respx.get(f"{base_url}/v1/agents/me").mock(return_value=httpx.Response(200, json={"status": "claimed"}))
        client.auth.status(fields="status,lp_balance")
        assert route.called
        assert "fields=status%2Clp_balance" in str(route.calls[0].request.url)

    @respx.mock
    def test_create_wallet_link_request(self, client: Client, base_url: str):
        route = respx.post(f"{base_url}/v1/link-wallet").mock(
            return_value=httpx.Response(
                200,
                json={
                    "nonce": "wl_abc",
                    "link_url": "https://app.alphakek.ai/link-wallet/wl_abc",
                    "expires_at": "2026-04-19T16:00:00+00:00",
                    "expires_in": 900,
                },
            )
        )
        result = client.auth.create_wallet_link_request()
        assert route.called
        assert result["nonce"] == "wl_abc"
        assert result["link_url"].endswith("wl_abc")

    @respx.mock
    def test_link_wallet(self, client: Client, base_url: str):
        route = respx.post(f"{base_url}/v1/agents/link-wallet").mock(
            return_value=httpx.Response(200, json={"wallet_address": "SoLWalletPubkey11111111111111111111111111111"})
        )
        result = client.auth.link_wallet(
            wallet_address="SoLWalletPubkey11111111111111111111111111111",
            signature="SigBase58Here",
        )
        assert route.called
        body = respx.calls.last.request.content.decode()
        assert "SoLWalletPubkey" in body
        assert "SigBase58Here" in body
        assert result["wallet_address"].startswith("SoL")


class TestBenchResource:
    @respx.mock
    def test_list(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/benches").mock(
            return_value=httpx.Response(
                200,
                json={"data": [{"name": "Test Bench", "token_address": "ABC123"}], "has_more": False},
            )
        )
        result = client.bench.list()
        assert result["has_more"] is False
        assert result["data"][0]["name"] == "Test Bench"

    @respx.mock
    def test_view(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/benches/ABC123").mock(
            return_value=httpx.Response(200, json={"name": "Test Bench", "token_address": "ABC123"})
        )
        result = client.bench.view("ABC123")
        assert result["name"] == "Test Bench"


class TestSubmissionResource:
    @respx.mock
    def test_next_challenge(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/challenges/next").mock(
            return_value=httpx.Response(200, json={"id": "ch-1", "title": "Test Challenge"})
        )
        result = client.submission.next_challenge()
        assert result is not None
        assert result["id"] == "ch-1"

    @respx.mock
    def test_next_challenge_returns_none_on_204(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/challenges/next").mock(return_value=httpx.Response(204))
        result = client.submission.next_challenge()
        assert result is None

    @respx.mock
    def test_create_submission(self, client: Client, base_url: str):
        respx.post(f"{base_url}/v1/submissions").mock(
            return_value=httpx.Response(201, json={"submission_id": "sub-1", "version": 1})
        )
        result = client.submission.create(
            challenge_id="ch-1",
            solution="My analysis of the research...",
            model_tag="claude-opus-4-6",
        )
        assert result["submission_id"] == "sub-1"

    @respx.mock
    def test_create_submission_dry_run(self, client: Client, base_url: str):
        route = respx.post(f"{base_url}/v1/submissions").mock(
            return_value=httpx.Response(200, json={"submission_id": None, "dry_run": True})
        )
        client.submission.create(
            challenge_id="ch-1",
            solution="Test solution",
            dry_run=True,
        )
        assert route.called
        assert "dry_run=true" in str(route.calls[0].request.url)


class TestOrchestratorResource:
    @respx.mock
    def test_query(self, client: Client, base_url: str):
        respx.post(f"{base_url}/v1/orchestrator/query").mock(
            return_value=httpx.Response(
                200, json={"results": [], "usage": {"lambda_cost": 0.1, "lambda_remaining": 99.9}}
            )
        )
        result = client.orchestrator.query(candidates=["Test content"], tokens=["7xKXtg"])
        assert "usage" in result

    @respx.mock
    def test_list(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/orchestrators").mock(
            return_value=httpx.Response(200, json={"data": [], "has_more": False})
        )
        result = client.orchestrator.list()
        assert result["has_more"] is False

    @respx.mock
    def test_info(self, client: Client, base_url: str):
        respx.get(f"{base_url}/v1/orchestrators/7xKXtg").mock(
            return_value=httpx.Response(200, json={"token_name": "Pizza", "version": 3, "status": "trained"})
        )
        result = client.orchestrator.info("7xKXtg")
        assert result["status"] == "trained"


class TestSchemaResource:
    @respx.mock
    def test_openapi(self, client: Client, base_url: str):
        respx.get(f"{base_url}/openapi.json").mock(
            return_value=httpx.Response(200, json={"openapi": "3.1.0", "paths": {}})
        )
        result = client.schema.openapi()
        assert result["openapi"] == "3.1.0"


class TestKnowledgeResource:
    @respx.mock
    def test_submit_returns_task_id(self, client: Client, base_url: str):
        import json

        route = respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={
                    "task_id": "11111111-2222-3333-4444-555555555555",
                    "status": "pending",
                    "poll_url": "/v2/knowledge/ask/11111111-2222-3333-4444-555555555555",
                },
            )
        )
        result = client.knowledge.submit("What is BTC?", search_mode="deep")
        assert result["task_id"] == "11111111-2222-3333-4444-555555555555"
        assert result["status"] == "pending"
        # search_mode must reach the wire; URL-only matching used to let an
        # accidental drop of the field pass silently.
        body = json.loads(route.calls[0].request.content)
        assert body == {"question": "What is BTC?", "search_mode": "deep"}

    @respx.mock
    def test_status_returns_state(self, client: Client, base_url: str):
        task_id = "11111111-2222-3333-4444-555555555555"
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "pending", "result": None})
        )
        result = client.knowledge.status(task_id)
        assert result["status"] == "pending"

    @respx.mock
    def test_ask_polls_until_succeeded(self, client: Client, base_url: str):
        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        # First GET: pending. Second GET: succeeded.
        get_route = respx.get(f"{base_url}/v2/knowledge/ask/{task_id}")
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
        result = client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert result["answer"] == "BTC."
        assert result["sources"] == ["https://x"]
        assert result["sentiment"] == 7

    @respx.mock
    def test_ask_raises_on_terminal_failure(self, client: Client, base_url: str):
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(
                200,
                json={"task_id": task_id, "status": "failed", "result": None, "error": "LLM timeout"},
            )
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert exc_info.value.task_id == task_id
        assert exc_info.value.status == "failed"
        assert "LLM timeout" in str(exc_info.value)

    @respx.mock
    def test_ask_raises_on_timeout(self, client: Client, base_url: str):
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        # Always returns pending — caller's timeout should fire.
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "running", "result": None})
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", timeout=0.0, poll_interval=0.0)
        assert exc_info.value.status == "timeout"
        assert exc_info.value.task_id == task_id

    @respx.mock
    def test_ask_raises_on_succeeded_with_no_result(self, client: Client, base_url: str):
        """Server bug: status=succeeded but result missing must surface, not hide."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "succeeded", "result": None})
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert exc_info.value.status == "succeeded_no_result"

    @respx.mock
    def test_ask_raises_on_submit_with_no_task_id(self, client: Client, base_url: str):
        """Defensive: if the server returns an unexpected shape, raise a typed
        error with the response body in it instead of a bare KeyError."""
        respx.post(f"{base_url}/v2/knowledge/ask").mock(return_value=httpx.Response(202, json={"unexpected": "shape"}))
        with pytest.raises(ValueError, match="no task_id"):
            client.knowledge.ask("What is BTC?", poll_interval=0.0)

    def test_ask_rejects_negative_poll_interval(self, client: Client):
        """Guard so the caller doesn't get a cryptic stdlib 'sleep length' error."""
        with pytest.raises(ValueError, match="poll_interval must be non-negative"):
            client.knowledge.ask("What is BTC?", poll_interval=-1.0)

    def test_ask_rejects_negative_timeout(self, client: Client):
        """A negative timeout would set the deadline in the past and produce
        a confusing 'timed out after -60s' message; reject up front."""
        with pytest.raises(ValueError, match="timeout must be non-negative"):
            client.knowledge.ask("What is BTC?", timeout=-1.0)

    @respx.mock
    def test_ask_raises_on_missing_status_field(self, client: Client, base_url: str):
        """Poll body without a ``status`` field is a server bug — surface as
        a 'missing status' error, not the misleading 'SDK may be out of date'."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id})
        )
        with pytest.raises(KnowledgeAskError, match="missing 'status' field"):
            client.knowledge.ask("What is BTC?", poll_interval=0.0)

    @respx.mock
    def test_ask_caps_per_request_timeout_to_remaining(self, client: Client, base_url: str):
        """Each poll GET must use a timeout no larger than what's left of the
        caller's overall ``timeout``. Prevents a slow server from making
        ``ask(timeout=N)`` exceed N when the per-request httpx default (30s)
        is larger than the caller's budget."""
        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        get_route = respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(
                200,
                json={
                    "task_id": task_id,
                    "status": "succeeded",
                    "result": {"answer": "ok", "sources": [], "sentiment": 5},
                },
            )
        )
        client.knowledge.ask("What is BTC?", timeout=2.0, poll_interval=0.0)
        # respx exposes the request that hit the wire; httpx attaches its
        # per-request timeout to the request extensions. The cap should be
        # ≤ 2s (the caller's overall budget), much less than httpx's 30s default.
        recorded_timeout = get_route.calls[0].request.extensions.get("timeout", {})
        # Read timeout is the relevant one for poll responses.
        read_timeout = recorded_timeout.get("read") if isinstance(recorded_timeout, dict) else None
        assert read_timeout is not None and read_timeout <= 2.0, (
            f"per-request read timeout was {read_timeout!r}, expected ≤ 2s"
        )

    @respx.mock
    def test_ask_converts_get_timeout_to_knowledge_ask_error(self, client: Client, base_url: str):
        """If httpx raises TimeoutException on a poll GET, ask() must convert
        to KnowledgeAskError(status='timeout') — the docstring contract is
        KnowledgeAskError | ValueError, no raw httpx exceptions."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(side_effect=httpx.ReadTimeout("slow"))
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", timeout=2.0, poll_interval=0.0)
        assert exc_info.value.status == "timeout"
        assert exc_info.value.task_id == task_id

    @respx.mock
    def test_ask_converts_submit_timeout_to_knowledge_ask_error(self, client: Client, base_url: str):
        """Submit POST timing out must surface as KnowledgeAskError."""
        from alphakek import KnowledgeAskError

        respx.post(f"{base_url}/v2/knowledge/ask").mock(side_effect=httpx.ConnectTimeout("slow"))
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", timeout=1.0, poll_interval=0.0)
        assert exc_info.value.status == "timeout"
        assert exc_info.value.task_id == ""

    @respx.mock
    def test_ask_caps_poll_sleep_to_remaining_timeout(self, client: Client, base_url: str):
        """ask(timeout=N, poll_interval=M>N) must respect ``timeout`` as the
        upper bound on total wall time, not extend it by ``poll_interval``."""
        import time as _time

        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "running", "result": None})
        )

        start = _time.monotonic()
        # 0.1s timeout, 5s poll_interval — without the fix the function would
        # sleep for ~5s after the first poll; with the cap it returns within
        # ~0.1s + a bit of overhead.
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", timeout=0.1, poll_interval=5.0)
        elapsed = _time.monotonic() - start
        assert exc_info.value.status == "timeout"
        assert elapsed < 1.0, f"ask() ignored timeout cap: {elapsed:.2f}s"

    @respx.mock
    def test_ask_raises_on_unknown_status(self, client: Client, base_url: str):
        """If the server adds a new terminal status before the SDK is updated,
        surface it immediately rather than polling until the local timeout."""
        from alphakek import KnowledgeAskError

        task_id = "11111111-2222-3333-4444-555555555555"
        respx.post(f"{base_url}/v2/knowledge/ask").mock(
            return_value=httpx.Response(
                202,
                json={"task_id": task_id, "status": "pending", "poll_url": f"/v2/knowledge/ask/{task_id}"},
            )
        )
        respx.get(f"{base_url}/v2/knowledge/ask/{task_id}").mock(
            return_value=httpx.Response(200, json={"task_id": task_id, "status": "cancelled", "result": None})
        )
        with pytest.raises(KnowledgeAskError) as exc_info:
            client.knowledge.ask("What is BTC?", poll_interval=0.0)
        assert "unexpected status 'cancelled'" in str(exc_info.value)
        assert exc_info.value.status == "failed"


class TestClientContextManager:
    @respx.mock
    def test_with_statement(self):
        with Client(api_key="alive_sk_test", base_url="https://test.com") as client:
            assert client._api_key == "alive_sk_test"

    def test_headers_include_auth(self):
        client = Client(api_key="alive_sk_test", base_url="https://test.com")
        headers = client._headers(auth=True)
        assert headers["Authorization"] == "Bearer alive_sk_test"
        client.close()

    def test_headers_skip_auth(self):
        client = Client(api_key="alive_sk_test", base_url="https://test.com")
        headers = client._headers(auth=False)
        assert "Authorization" not in headers
        client.close()
