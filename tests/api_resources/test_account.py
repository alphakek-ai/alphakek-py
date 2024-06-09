# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from alphakek import Alphakek, AsyncAlphakek
from tests.utils import assert_matches_type
from alphakek.types import User

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAccount:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_info(self, client: Alphakek) -> None:
        account = client.account.info()
        assert_matches_type(User, account, path=["response"])

    @parametrize
    def test_raw_response_info(self, client: Alphakek) -> None:
        response = client.account.with_raw_response.info()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = response.parse()
        assert_matches_type(User, account, path=["response"])

    @parametrize
    def test_streaming_response_info(self, client: Alphakek) -> None:
        with client.account.with_streaming_response.info() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = response.parse()
            assert_matches_type(User, account, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncAccount:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_info(self, async_client: AsyncAlphakek) -> None:
        account = await async_client.account.info()
        assert_matches_type(User, account, path=["response"])

    @parametrize
    async def test_raw_response_info(self, async_client: AsyncAlphakek) -> None:
        response = await async_client.account.with_raw_response.info()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        account = await response.parse()
        assert_matches_type(User, account, path=["response"])

    @parametrize
    async def test_streaming_response_info(self, async_client: AsyncAlphakek) -> None:
        async with async_client.account.with_streaming_response.info() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            account = await response.parse()
            assert_matches_type(User, account, path=["response"])

        assert cast(Any, response.is_closed) is True
