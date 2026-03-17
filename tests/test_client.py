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
