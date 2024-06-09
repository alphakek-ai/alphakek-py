# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from alphakek import Alphakek, AsyncAlphakek
from tests.utils import assert_matches_type
from alphakek.types import (
    KnowledgeDocumentView,
    KnowledgeSearchResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestKnowledge:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_get_by_link(self, client: Alphakek) -> None:
        knowledge = client.knowledge.get_by_link(
            link="string",
        )
        assert_matches_type(KnowledgeDocumentView, knowledge, path=["response"])

    @parametrize
    def test_raw_response_get_by_link(self, client: Alphakek) -> None:
        response = client.knowledge.with_raw_response.get_by_link(
            link="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge = response.parse()
        assert_matches_type(KnowledgeDocumentView, knowledge, path=["response"])

    @parametrize
    def test_streaming_response_get_by_link(self, client: Alphakek) -> None:
        with client.knowledge.with_streaming_response.get_by_link(
            link="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge = response.parse()
            assert_matches_type(KnowledgeDocumentView, knowledge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_search(self, client: Alphakek) -> None:
        knowledge = client.knowledge.search(
            query="string",
        )
        assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

    @parametrize
    def test_method_search_with_all_params(self, client: Alphakek) -> None:
        knowledge = client.knowledge.search(
            query="string",
            count=1,
            offset=0,
            sort_by="relevance",
            sources=["news", "4chan"],
        )
        assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

    @parametrize
    def test_raw_response_search(self, client: Alphakek) -> None:
        response = client.knowledge.with_raw_response.search(
            query="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge = response.parse()
        assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

    @parametrize
    def test_streaming_response_search(self, client: Alphakek) -> None:
        with client.knowledge.with_streaming_response.search(
            query="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge = response.parse()
            assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncKnowledge:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_get_by_link(self, async_client: AsyncAlphakek) -> None:
        knowledge = await async_client.knowledge.get_by_link(
            link="string",
        )
        assert_matches_type(KnowledgeDocumentView, knowledge, path=["response"])

    @parametrize
    async def test_raw_response_get_by_link(self, async_client: AsyncAlphakek) -> None:
        response = await async_client.knowledge.with_raw_response.get_by_link(
            link="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge = await response.parse()
        assert_matches_type(KnowledgeDocumentView, knowledge, path=["response"])

    @parametrize
    async def test_streaming_response_get_by_link(self, async_client: AsyncAlphakek) -> None:
        async with async_client.knowledge.with_streaming_response.get_by_link(
            link="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge = await response.parse()
            assert_matches_type(KnowledgeDocumentView, knowledge, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_search(self, async_client: AsyncAlphakek) -> None:
        knowledge = await async_client.knowledge.search(
            query="string",
        )
        assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncAlphakek) -> None:
        knowledge = await async_client.knowledge.search(
            query="string",
            count=1,
            offset=0,
            sort_by="relevance",
            sources=["news", "4chan"],
        )
        assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

    @parametrize
    async def test_raw_response_search(self, async_client: AsyncAlphakek) -> None:
        response = await async_client.knowledge.with_raw_response.search(
            query="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        knowledge = await response.parse()
        assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncAlphakek) -> None:
        async with async_client.knowledge.with_streaming_response.search(
            query="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            knowledge = await response.parse()
            assert_matches_type(KnowledgeSearchResponse, knowledge, path=["response"])

        assert cast(Any, response.is_closed) is True
