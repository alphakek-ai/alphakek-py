"""Tests for CLI commands using Typer's CliRunner."""

import json
from unittest.mock import MagicMock, patch

import httpx
from typer.testing import CliRunner

from alphakek.cli.main import app

runner = CliRunner()


class TestVersionCommand:
    def test_version_output(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "version" in data


class TestAuthRegister:
    @patch("alphakek.cli.main._make_client")
    @patch("alphakek._credentials.save_credentials")
    def test_register_with_name(self, mock_save, mock_make):
        mock_client = MagicMock()
        mock_client.auth.register.return_value = {
            "agent_id": "abc-123",
            "api_key": "alive_sk_new",
            "verification_code": "ALIVE-XYZ",
            "claim_url": "https://alive.alphakek.ai/claim/ALIVE-XYZ",
            "next_steps": "Send claim_url to your human.",
        }
        mock_make.return_value = mock_client
        mock_save.return_value = "/home/test/creds.json"

        result = runner.invoke(app, ["auth", "register", "--name", "TestAgent"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["api_key"] == "alive_sk_new"

    def test_register_without_name_errors(self):
        result = runner.invoke(app, ["auth", "register"])
        assert result.exit_code != 0


class TestAuthStatus:
    @patch("alphakek.cli.main._make_client")
    def test_status(self, mock_make):
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {
            "id": "abc-123",
            "name": "TestAgent",
            "status": "claimed",
            "lp_balance": 42.0,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["auth", "status"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["status"] == "claimed"


class TestBenchList:
    @patch("alphakek.cli.main._make_client")
    def test_list_benches(self, mock_make):
        mock_client = MagicMock()
        mock_client.bench.list.return_value = {
            "tokens": [{"name": "Bench A"}],
            "total": 1,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["bench", "list"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["total"] == 1


class TestBenchView:
    @patch("alphakek.cli.main._make_client")
    def test_view_bench(self, mock_make):
        mock_client = MagicMock()
        mock_client.bench.view.return_value = {
            "name": "Bench A",
            "token_address": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["bench", "view", "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["name"] == "Bench A"


class TestSubmissionNextChallenge:
    @patch("alphakek.cli.main._make_client")
    def test_next_challenge_returns_json(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.next_challenge.return_value = {
            "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
            "title": "Analyze tokenomics",
            "research_context": "Examine the token distribution...",
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["id"] == "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
        assert data["title"] == "Analyze tokenomics"

    @patch("alphakek.cli.main._make_client")
    def test_next_challenge_with_bench_filter(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.next_challenge.return_value = {"id": "ch-1", "title": "Bench-specific challenge"}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge", "--bench", "7xKXtg"])
        assert result.exit_code == 0
        mock_client.submission.next_challenge.assert_called_once_with(bench="7xKXtg")

    @patch("alphakek.cli.main._make_client")
    def test_next_challenge_none_returns_null_exit_1(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.next_challenge.return_value = None
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge"])
        assert result.exit_code == 1
        assert result.stdout.strip() == "null"

    @patch("alphakek.cli.main._make_client")
    def test_next_challenge_http_error(self, mock_make):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"detail": "Unauthorized"}'
        mock_client.submission.next_challenge.side_effect = httpx.HTTPStatusError(
            "401", request=MagicMock(), response=mock_response
        )
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge"])
        assert result.exit_code != 0

    @patch("alphakek.cli.main._make_client")
    def test_next_challenge_network_error(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.next_challenge.side_effect = httpx.RequestError("Connection refused")
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge"])
        assert result.exit_code != 0


class TestSubmissionCreate:
    @patch("alphakek.cli.main._make_client")
    def test_create_with_auto_challenge(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.next_challenge.return_value = {"id": "ch-1", "title": "Test Challenge"}
        mock_client.submission.create.return_value = {"submission_id": "sub-1", "version": 1}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "create", "--solution", "My analysis"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["submission_id"] == "sub-1"

    @patch("alphakek.cli.main._make_client")
    def test_create_with_explicit_challenge(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.create.return_value = {"submission_id": "sub-1"}
        mock_make.return_value = mock_client

        result = runner.invoke(
            app,
            ["submission", "create", "--challenge", "ch-1", "--solution", "Analysis", "--model", "claude-opus-4-6"],
        )
        assert result.exit_code == 0

    @patch("alphakek.cli.main._make_client")
    def test_create_with_json_input(self, mock_make):
        mock_client = MagicMock()
        mock_client.submission.create.return_value = {"submission_id": "sub-1"}
        mock_make.return_value = mock_client

        body = json.dumps({"challenge_id": "ch-1", "solution": "My solution", "model_tag": "test"})
        result = runner.invoke(app, ["submission", "create", "--json", body])
        assert result.exit_code == 0

    def test_create_without_solution_errors(self):
        result = runner.invoke(app, ["submission", "create"])
        assert result.exit_code != 0


class TestOrchestratorEvaluate:
    @patch("alphakek.cli.main._make_client")
    def test_evaluate_with_flags(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.evaluate.return_value = {
            "score": 0.85,
            "tldr": "Good analysis",
            "lp_cost": 10.0,
            "lp_remaining": 32.0,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["orchestrator", "evaluate", "--bench", "7xKXtg", "--content", "Test content"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["score"] == 0.85

    @patch("alphakek.cli.main._make_client")
    def test_evaluate_with_json(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.evaluate.return_value = {"score": 0.9, "tldr": "Great"}
        mock_make.return_value = mock_client

        body = json.dumps({"token_address": "7xKXtg", "content": "Test", "fields": "score,tldr"})
        result = runner.invoke(app, ["orchestrator", "evaluate", "--json", body])
        assert result.exit_code == 0

    def test_evaluate_without_bench_errors(self):
        result = runner.invoke(app, ["orchestrator", "evaluate", "--content", "Test"])
        assert result.exit_code != 0

    def test_evaluate_without_content_errors(self):
        result = runner.invoke(app, ["orchestrator", "evaluate", "--bench", "7xKXtg"])
        assert result.exit_code != 0


class TestOrchestratorList:
    @patch("alphakek.cli.main._make_client")
    def test_list_orchestrators(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.list.return_value = {
            "harnesses": [{"token_name": "Pizza", "status": "trained"}],
            "total": 1,
            "has_more": False,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["orchestrator", "list"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["total"] == 1


class TestOrchestratorInfo:
    @patch("alphakek.cli.main._make_client")
    def test_info(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.info.return_value = {
            "token_name": "Pizza",
            "version": 3,
            "status": "trained",
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["orchestrator", "info", "7xKXtg"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["status"] == "trained"


class TestSchemaCommand:
    @patch("alphakek.cli.main._make_client")
    def test_list_all_endpoints(self, mock_make):
        mock_client = MagicMock()
        mock_client.schema.openapi.return_value = {
            "openapi": "3.1.0",
            "paths": {
                "/v1/agents/register": {"post": {"summary": "Register agent"}},
                "/next/challenge": {"get": {"summary": "Get next challenge"}},
            },
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["schema"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["total"] == 2

    @patch("alphakek.cli.main._make_client")
    def test_specific_command(self, mock_make):
        mock_client = MagicMock()
        mock_client.schema.openapi.return_value = {
            "openapi": "3.1.0",
            "paths": {
                "/v1/agents/register": {
                    "post": {
                        "summary": "Register agent",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {"type": "object", "properties": {"name": {"type": "string"}}},
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Success", "content": {"application/json": {"schema": {}}}}
                        },
                    }
                },
            },
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["schema", "auth.register"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["method"] == "POST"
        assert data["path"] == "/v1/agents/register"
