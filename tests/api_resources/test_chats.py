# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from alphakek import Alphakek, AsyncAlphakek
from tests.utils import assert_matches_type
from alphakek.types import ChatCompletion

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestChats:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_completions(self, client: Alphakek) -> None:
        chat = client.chats.completions(
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
        assert_matches_type(ChatCompletion, chat, path=["response"])

    @parametrize
    def test_method_completions_with_all_params(self, client: Alphakek) -> None:
        chat = client.chats.completions(
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
        assert_matches_type(ChatCompletion, chat, path=["response"])

    @parametrize
    def test_raw_response_completions(self, client: Alphakek) -> None:
        response = client.chats.with_raw_response.completions(
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
        chat = response.parse()
        assert_matches_type(ChatCompletion, chat, path=["response"])

    @parametrize
    def test_streaming_response_completions(self, client: Alphakek) -> None:
        with client.chats.with_streaming_response.completions(
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

            chat = response.parse()
            assert_matches_type(ChatCompletion, chat, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncChats:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    async def test_method_completions(self, async_client: AsyncAlphakek) -> None:
        chat = await async_client.chats.completions(
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
        assert_matches_type(ChatCompletion, chat, path=["response"])

    @parametrize
    async def test_method_completions_with_all_params(self, async_client: AsyncAlphakek) -> None:
        chat = await async_client.chats.completions(
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
        assert_matches_type(ChatCompletion, chat, path=["response"])

    @parametrize
    async def test_raw_response_completions(self, async_client: AsyncAlphakek) -> None:
        response = await async_client.chats.with_raw_response.completions(
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
        chat = await response.parse()
        assert_matches_type(ChatCompletion, chat, path=["response"])

    @parametrize
    async def test_streaming_response_completions(self, async_client: AsyncAlphakek) -> None:
        async with async_client.chats.with_streaming_response.completions(
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

            chat = await response.parse()
            assert_matches_type(ChatCompletion, chat, path=["response"])

        assert cast(Any, response.is_closed) is True
