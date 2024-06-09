# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from alphakek import Alphakek, AsyncAlphakek
from tests.utils import assert_matches_type
from alphakek.types import KnowledgeDocumentView

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestGet:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_by_link(self, client: Alphakek) -> None:
        get = client.knowledge.get.by_link(
            link="string",
        )
        assert_matches_type(KnowledgeDocumentView, get, path=["response"])

    @parametrize
    def test_raw_response_by_link(self, client: Alphakek) -> None:
        response = client.knowledge.get.with_raw_response.by_link(
            link="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        get = response.parse()
        assert_matches_type(KnowledgeDocumentView, get, path=["response"])

    @parametrize
    def test_streaming_response_by_link(self, client: Alphakek) -> None:
        with client.knowledge.get.with_streaming_response.by_link(
            link="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            get = response.parse()
            assert_matches_type(KnowledgeDocumentView, get, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncGet:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_by_link(self, async_client: AsyncAlphakek) -> None:
        get = await async_client.knowledge.get.by_link(
            link="string",
        )
        assert_matches_type(KnowledgeDocumentView, get, path=["response"])

    @parametrize
    async def test_raw_response_by_link(self, async_client: AsyncAlphakek) -> None:
        response = await async_client.knowledge.get.with_raw_response.by_link(
            link="string",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        get = await response.parse()
        assert_matches_type(KnowledgeDocumentView, get, path=["response"])

    @parametrize
    async def test_streaming_response_by_link(self, async_client: AsyncAlphakek) -> None:
        async with async_client.knowledge.get.with_streaming_response.by_link(
            link="string",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            get = await response.parse()
            assert_matches_type(KnowledgeDocumentView, get, path=["response"])

        assert cast(Any, response.is_closed) is True
