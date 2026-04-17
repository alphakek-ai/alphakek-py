"""Tests for CLI commands using Typer's CliRunner."""

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from typer.testing import CliRunner

from alphakek.cli.main import app


def _has_solders() -> bool:
    try:
        import solders  # noqa: F401
    except ImportError:
        return False
    return True


# Tests that patch `alphakek.signing.*` require the optional `solana` extra —
# `alphakek.signing` imports solders at module load. Without the extra, CI's
# `uv sync --locked` skips solders, so these patches can't resolve.
requires_solana = pytest.mark.skipif(not _has_solders(), reason="requires 'solana' extra (solders)")

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


class TestAuthLinkWallet:
    def test_requires_key_or_signature(self):
        result = runner.invoke(app, ["auth", "link-wallet"])
        assert result.exit_code != 0
        # _error writes JSON error to stderr and exits nonzero. CliRunner captures
        # combined output on .output in recent Typer/Click. Assert on exit code.

    def test_signature_requires_wallet_address(self):
        result = runner.invoke(app, ["auth", "link-wallet", "--signature", "sig123"])
        assert result.exit_code != 0

    @patch("alphakek.cli.main._make_client")
    def test_link_with_precomputed_signature(self, mock_make):
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"agent": {"id": "abc-123"}}
        mock_client.auth.link_wallet.return_value = {"wallet_address": "SoLPubkey"}
        mock_make.return_value = mock_client

        result = runner.invoke(
            app,
            ["auth", "link-wallet", "--wallet-address", "SoLPubkey", "--signature", "SigBase58"],
        )
        assert result.exit_code == 0
        mock_client.auth.link_wallet.assert_called_once_with(wallet_address="SoLPubkey", signature="SigBase58")
        data = json.loads(result.stdout)
        assert data["wallet_address"] == "SoLPubkey"

    @patch("alphakek.cli.main._make_client")
    def test_link_uses_explicit_agent_id(self, mock_make):
        # When --agent-id is passed, no /v1/agents/me round trip.
        mock_client = MagicMock()
        mock_client.auth.link_wallet.return_value = {"wallet_address": "SoLPubkey"}
        mock_make.return_value = mock_client

        result = runner.invoke(
            app,
            [
                "auth",
                "link-wallet",
                "--wallet-address",
                "SoLPubkey",
                "--signature",
                "SigBase58",
                "--agent-id",
                "explicit-id",
            ],
        )
        assert result.exit_code == 0
        mock_client.auth.status.assert_not_called()

    @requires_solana
    @patch("alphakek.signing.sign_link_message")
    @patch("alphakek.signing.load_keypair")
    @patch("alphakek.cli.main._make_client")
    def test_link_reads_private_key_from_stdin(self, mock_make, mock_load, mock_sign):
        mock_client = MagicMock()
        mock_client.auth.link_wallet.return_value = {"wallet_address": "DerivedPubkey"}
        mock_make.return_value = mock_client
        mock_load.return_value = MagicMock()
        mock_sign.return_value = ("DerivedPubkey", "SigFromKeypair")

        # '-' must read from stdin and not pollute argv.
        result = runner.invoke(
            app,
            ["auth", "link-wallet", "--private-key", "-", "--agent-id", "abc-123"],
            input="SECRET_FROM_STDIN\n",
        )
        assert result.exit_code == 0
        mock_load.assert_called_once_with("SECRET_FROM_STDIN")
        mock_client.auth.link_wallet.assert_called_once_with(wallet_address="DerivedPubkey", signature="SigFromKeypair")

    @requires_solana
    @patch("alphakek.signing.sign_link_message")
    @patch("alphakek.signing.load_keypair")
    @patch("alphakek.cli.main._make_client")
    def test_link_reads_private_key_from_env(self, mock_make, mock_load, mock_sign, monkeypatch):
        mock_client = MagicMock()
        mock_client.auth.link_wallet.return_value = {"wallet_address": "DerivedPubkey"}
        mock_make.return_value = mock_client
        mock_load.return_value = MagicMock()
        mock_sign.return_value = ("DerivedPubkey", "SigFromKeypair")

        monkeypatch.setenv("ALPHAKEK_SIGNING_KEY", "SECRET_FROM_ENV")
        result = runner.invoke(app, ["auth", "link-wallet", "--agent-id", "abc-123"])
        assert result.exit_code == 0
        mock_load.assert_called_once_with("SECRET_FROM_ENV")


class TestGlobalPluck:
    @patch("alphakek.cli.main._make_client")
    def test_pluck_scalar_prints_raw(self, mock_make):
        # --pluck id should print the scalar without JSON quotes.
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"id": "abc-123", "status": "claimed"}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "id", "auth", "status"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "abc-123"

    @patch("alphakek.cli.main._make_client")
    def test_pluck_nested_path(self, mock_make):
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"agent": {"id": "abc-123", "name": "A2"}}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "agent.name", "auth", "status"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "A2"

    @patch("alphakek.cli.main._make_client")
    def test_pluck_list_index(self, mock_make):
        mock_client = MagicMock()
        mock_client.bench.list.return_value = {
            "data": [{"token_address": "TOK_A"}, {"token_address": "TOK_B"}],
            "has_more": False,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "data.0.token_address", "bench", "list"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "TOK_A"

    @patch("alphakek.cli.main._make_client")
    def test_pluck_bool_prints_lowercase(self, mock_make):
        # Shell-idiomatic true/false (not Python's True/False or JSON's true/false quoted).
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"wallet_linked": True}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "wallet_linked", "auth", "status"])
        assert result.exit_code == 0
        assert result.stdout.strip() == "true"

    @patch("alphakek.cli.main._make_client")
    def test_pluck_nonscalar_prints_compact_json(self, mock_make):
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"agent": {"id": "abc", "name": "A"}}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "agent", "auth", "status"])
        assert result.exit_code == 0
        # Not indented (compact) — pluck is for scripting, not display.
        assert result.stdout.strip() == '{"id": "abc", "name": "A"}'

    @patch("alphakek.cli.main._make_client")
    def test_pluck_missing_key_exits_3(self, mock_make):
        # Exit 3 is distinct from 1 (error) so scripts can detect schema drift.
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"status": "claimed"}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "nonexistent", "auth", "status"])
        assert result.exit_code == 3

    @patch("alphakek.cli.main._make_client")
    def test_pluck_deep_missing_exits_3(self, mock_make):
        mock_client = MagicMock()
        mock_client.auth.status.return_value = {"agent": {"id": "abc"}}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "agent.missing.deeper", "auth", "status"])
        assert result.exit_code == 3

    @patch("alphakek.cli.main._make_client")
    def test_pluck_index_out_of_range_exits_3(self, mock_make):
        mock_client = MagicMock()
        mock_client.bench.list.return_value = {"data": [{"x": 1}], "has_more": False}
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["--pluck", "data.5.x", "bench", "list"])
        assert result.exit_code == 3


class TestValidateNextExitCode:
    @patch("alphakek.cli.main._make_client")
    def test_next_pair_none_returns_null_exit_2(self, mock_make):
        mock_client = MagicMock()
        mock_client.validation.next_pair.return_value = None
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["validate", "next"])
        assert result.exit_code == 2
        assert result.stdout.strip() == "null"

    @patch("alphakek.cli.main._make_client")
    def test_next_pair_success_exit_0(self, mock_make):
        mock_client = MagicMock()
        mock_client.validation.next_pair.return_value = {
            "challenge_id": "c1",
            "solution_a_id": "sa",
            "solution_b_id": "sb",
            "solution_a_text": "...",
            "solution_b_text": "...",
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["validate", "next"])
        assert result.exit_code == 0


class TestBenchList:
    @patch("alphakek.cli.main._make_client")
    def test_list_benches(self, mock_make):
        mock_client = MagicMock()
        mock_client.bench.list.return_value = {
            "data": [{"name": "Bench A"}],
            "has_more": False,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["bench", "list"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["has_more"] is False


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
    def test_next_challenge_none_returns_null_exit_2(self, mock_make):
        # Exit code 2 = "no data available" (empty queue) — distinct from 1 = error.
        mock_client = MagicMock()
        mock_client.submission.next_challenge.return_value = None
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge"])
        assert result.exit_code == 2
        assert result.stdout.strip() == "null"

    @patch("alphakek.cli.main._make_client")
    def test_next_challenge_http_error(self, mock_make):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = '{"detail": "Unauthorized"}'
        mock_response.json.return_value = {"detail": "Unauthorized"}
        mock_client.submission.next_challenge.side_effect = httpx.HTTPStatusError(
            "401", request=MagicMock(), response=mock_response
        )
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["submission", "next-challenge"])
        assert result.exit_code != 0
        # Verify the detail is extracted from API JSON, not double-encoded
        error = json.loads(result.output)
        assert error["detail"] == "Failed to fetch challenge: Unauthorized"
        assert error["status"] == 401

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


class TestOrchestratorQuery:
    @patch("alphakek.cli.main._make_client")
    def test_query_with_flags(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.query.return_value = {
            "results": [{"token_address": "7xKXtg", "candidates": [{"score": 0.85}], "ranked_indices": [0]}],
            "usage": {"lambda_cost": 0.1, "lambda_remaining": 32.0},
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["orchestrator", "query", "--bench", "7xKXtg", "--content", "Test content"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "results" in data

    @patch("alphakek.cli.main._make_client")
    def test_query_with_json(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.query.return_value = {
            "results": [],
            "usage": {"lambda_cost": 0.1, "lambda_remaining": 99.9},
        }
        mock_make.return_value = mock_client

        body = json.dumps(
            {
                "candidates": [{"type": "text", "content": "Test"}],
                "tokens": [{"address": "7xKXtg"}],
            }
        )
        result = runner.invoke(app, ["orchestrator", "query", "--json", body])
        assert result.exit_code == 0

    def test_query_without_bench_errors(self):
        result = runner.invoke(app, ["orchestrator", "query", "--content", "Test"])
        assert result.exit_code != 0

    def test_query_without_content_errors(self):
        result = runner.invoke(app, ["orchestrator", "query", "--bench", "7xKXtg"])
        assert result.exit_code != 0


class TestOrchestratorList:
    @patch("alphakek.cli.main._make_client")
    def test_list_orchestrators(self, mock_make):
        mock_client = MagicMock()
        mock_client.orchestrator.list.return_value = {
            "data": [{"token_name": "Pizza", "status": "trained"}],
            "has_more": False,
        }
        mock_make.return_value = mock_client

        result = runner.invoke(app, ["orchestrator", "list"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["has_more"] is False


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
                "/v1/challenges/next": {"get": {"summary": "Get next challenge"}},
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
