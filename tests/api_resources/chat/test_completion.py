# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from alphakek import Alphakek, AsyncAlphakek
from tests.utils import assert_matches_type
from alphakek.types.chat import ChatCompletion

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCompletion:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Alphakek) -> None:
        completion = client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Alphakek) -> None:
        completion = client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
            persona="string",
            stream=True,
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Alphakek) -> None:
        response = client.chat.completion.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Alphakek) -> None:
        with client.chat.completion.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = response.parse()
            assert_matches_type(ChatCompletion, completion, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncCompletion:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_create(self, async_client: AsyncAlphakek) -> None:
        completion = await async_client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncAlphakek) -> None:
        completion = await async_client.chat.completion.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
            persona="string",
            stream=True,
        )
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncAlphakek) -> None:
        response = await async_client.chat.completion.with_raw_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        completion = await response.parse()
        assert_matches_type(ChatCompletion, completion, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncAlphakek) -> None:
        async with async_client.chat.completion.with_streaming_response.create(
            messages=[
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
                {
                    "role": "system",
                    "content": "string",
                },
            ],
            model="versa",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            completion = await response.parse()
            assert_matches_type(ChatCompletion, completion, path=["response"])

        assert cast(Any, response.is_closed) is True
