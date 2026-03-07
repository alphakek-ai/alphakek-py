"""Tests for AsyncClient using respx."""

import httpx
import pytest
import respx

from alphakek.client import AsyncClient

BASE = "https://alive-api.alphakek.ai"


@pytest.fixture
def client():
    return AsyncClient(api_key="alive_sk_test", base_url=BASE)


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
        respx.get(f"{BASE}/alive-tokens").mock(
            return_value=httpx.Response(200, json={"tokens": [{"name": "Bench A"}], "total": 1})
        )
        result = await client.bench.list()
        assert result["total"] == 1

    @respx.mock
    async def test_view(self, client):
        addr = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
        respx.get(f"{BASE}/alive-tokens/{addr}").mock(
            return_value=httpx.Response(200, json={"name": "Bench A", "token_address": addr})
        )
        result = await client.bench.view(addr)
        assert result["name"] == "Bench A"


class TestAsyncSubmissionResource:
    @respx.mock
    async def test_next_challenge(self, client):
        respx.get(f"{BASE}/next/challenge").mock(return_value=httpx.Response(200, json={"id": "ch-1", "title": "Test"}))
        result = await client.submission.next_challenge()
        assert result["id"] == "ch-1"

    @respx.mock
    async def test_next_challenge_returns_none_on_204(self, client):
        respx.get(f"{BASE}/next/challenge").mock(return_value=httpx.Response(204))
        result = await client.submission.next_challenge()
        assert result is None

    @respx.mock
    async def test_create_submission(self, client):
        respx.post(f"{BASE}/next/submit").mock(
            return_value=httpx.Response(200, json={"submission_id": "sub-1", "version": 1})
        )
        result = await client.submission.create(challenge_id="ch-1", solution="My analysis")
        assert result["submission_id"] == "sub-1"


class TestAsyncSchemaResource:
    @respx.mock
    async def test_openapi(self, client):
        respx.get(f"{BASE}/openapi.json").mock(return_value=httpx.Response(200, json={"openapi": "3.1.0", "paths": {}}))
        result = await client.schema.openapi()
        assert result["openapi"] == "3.1.0"


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
