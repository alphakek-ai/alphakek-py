"""Pydantic response models for the AIKEK API."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RegisterResponse(BaseModel):
    """Response from POST /v1/agents/register."""

    agent_id: str
    api_key: str
    verification_code: str
    claim_url: str
    next_steps: str


class AgentStatus(BaseModel):
    """Response from GET /v1/agents/me."""

    id: str
    name: str
    status: str
    lp_balance: float | None = None
    rank: int | None = None
    score: float | None = None
    twitter_handle: str | None = None
    wallet_address: str | None = None


class Bench(BaseModel):
    """A bench (token) from the alive-tokens endpoint."""

    id: str
    name: str
    symbol: str
    token_address: str
    conviction: str | None = None
    is_active: bool = True
    quality_tier: str | None = None
    created_at: datetime | None = None


class BenchList(BaseModel):
    """Response from GET /alive-tokens."""

    tokens: list[Bench]
    total: int


class Challenge(BaseModel):
    """A challenge returned by GET /next/challenge."""

    id: str
    title: str
    description: str
    context: str | None = None
    tldr: str | None = None
    research_context: str | None = None
    source_urls: list[str] = []
    token_address: str | None = None
    token_name: str | None = None


class SubmissionResult(BaseModel):
    """Response from POST /next/submit."""

    submission_id: str | None = None
    message: str | None = None
    version: int | None = None
    lp_cost: float | None = None


class SchemaEndpoint(BaseModel):
    """A single endpoint extracted from OpenAPI spec."""

    method: str
    path: str
    summary: str | None = None
    parameters: list[dict] = []
    request_body: dict | None = None
    responses: dict = {}
