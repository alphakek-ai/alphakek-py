# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from alphakek import Alphakek, AsyncAlphakek
from alphakek._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestVisuals:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_apply_effect(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = client.visuals.apply_effect(
            image=b"raw file contents",
            prompt="string",
        )
        assert visual.is_closed
        assert visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_apply_effect_with_all_params(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = client.visuals.apply_effect(
            image=b"raw file contents",
            prompt="string",
            allow_nsfw=True,
            seed=0,
        )
        assert visual.is_closed
        assert visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_apply_effect(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        visual = client.visuals.with_raw_response.apply_effect(
            image=b"raw file contents",
            prompt="string",
        )

        assert visual.is_closed is True
        assert visual.http_request.headers.get("X-Stainless-Lang") == "python"
        assert visual.json() == {"foo": "bar"}
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_apply_effect(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.visuals.with_streaming_response.apply_effect(
            image=b"raw file contents",
            prompt="string",
        ) as visual:
            assert not visual.is_closed
            assert visual.http_request.headers.get("X-Stainless-Lang") == "python"

            assert visual.json() == {"foo": "bar"}
            assert cast(Any, visual.is_closed) is True
            assert isinstance(visual, StreamedBinaryAPIResponse)

        assert cast(Any, visual.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_apply_mirage(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = client.visuals.apply_mirage(
            image=b"raw file contents",
            prompt="string",
        )
        assert visual.is_closed
        assert visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_apply_mirage_with_all_params(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = client.visuals.apply_mirage(
            image=b"raw file contents",
            prompt="string",
            allow_nsfw=True,
            seed=0,
        )
        assert visual.is_closed
        assert visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_apply_mirage(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        visual = client.visuals.with_raw_response.apply_mirage(
            image=b"raw file contents",
            prompt="string",
        )

        assert visual.is_closed is True
        assert visual.http_request.headers.get("X-Stainless-Lang") == "python"
        assert visual.json() == {"foo": "bar"}
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_apply_mirage(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.visuals.with_streaming_response.apply_mirage(
            image=b"raw file contents",
            prompt="string",
        ) as visual:
            assert not visual.is_closed
            assert visual.http_request.headers.get("X-Stainless-Lang") == "python"

            assert visual.json() == {"foo": "bar"}
            assert cast(Any, visual.is_closed) is True
            assert isinstance(visual, StreamedBinaryAPIResponse)

        assert cast(Any, visual.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_image(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = client.visuals.create_image(
            allow_nsfw=True,
            prompt="string",
        )
        assert visual.is_closed
        assert visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_image_with_all_params(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = client.visuals.create_image(
            allow_nsfw=True,
            prompt="string",
            height=512,
            seed=0,
            width=512,
        )
        assert visual.is_closed
        assert visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create_image(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        visual = client.visuals.with_raw_response.create_image(
            allow_nsfw=True,
            prompt="string",
        )

        assert visual.is_closed is True
        assert visual.http_request.headers.get("X-Stainless-Lang") == "python"
        assert visual.json() == {"foo": "bar"}
        assert isinstance(visual, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create_image(self, client: Alphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.visuals.with_streaming_response.create_image(
            allow_nsfw=True,
            prompt="string",
        ) as visual:
            assert not visual.is_closed
            assert visual.http_request.headers.get("X-Stainless-Lang") == "python"

            assert visual.json() == {"foo": "bar"}
            assert cast(Any, visual.is_closed) is True
            assert isinstance(visual, StreamedBinaryAPIResponse)

        assert cast(Any, visual.is_closed) is True


class TestAsyncVisuals:
    parametrize = pytest.mark.parametrize("async_client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_apply_effect(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = await async_client.visuals.apply_effect(
            image=b"raw file contents",
            prompt="string",
        )
        assert visual.is_closed
        assert await visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_apply_effect_with_all_params(
        self, async_client: AsyncAlphakek, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = await async_client.visuals.apply_effect(
            image=b"raw file contents",
            prompt="string",
            allow_nsfw=True,
            seed=0,
        )
        assert visual.is_closed
        assert await visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_apply_effect(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        visual = await async_client.visuals.with_raw_response.apply_effect(
            image=b"raw file contents",
            prompt="string",
        )

        assert visual.is_closed is True
        assert visual.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await visual.json() == {"foo": "bar"}
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_apply_effect(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_effect").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.visuals.with_streaming_response.apply_effect(
            image=b"raw file contents",
            prompt="string",
        ) as visual:
            assert not visual.is_closed
            assert visual.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await visual.json() == {"foo": "bar"}
            assert cast(Any, visual.is_closed) is True
            assert isinstance(visual, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, visual.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_apply_mirage(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = await async_client.visuals.apply_mirage(
            image=b"raw file contents",
            prompt="string",
        )
        assert visual.is_closed
        assert await visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_apply_mirage_with_all_params(
        self, async_client: AsyncAlphakek, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = await async_client.visuals.apply_mirage(
            image=b"raw file contents",
            prompt="string",
            allow_nsfw=True,
            seed=0,
        )
        assert visual.is_closed
        assert await visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_apply_mirage(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        visual = await async_client.visuals.with_raw_response.apply_mirage(
            image=b"raw file contents",
            prompt="string",
        )

        assert visual.is_closed is True
        assert visual.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await visual.json() == {"foo": "bar"}
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_apply_mirage(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/apply_mirage").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.visuals.with_streaming_response.apply_mirage(
            image=b"raw file contents",
            prompt="string",
        ) as visual:
            assert not visual.is_closed
            assert visual.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await visual.json() == {"foo": "bar"}
            assert cast(Any, visual.is_closed) is True
            assert isinstance(visual, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, visual.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_image(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = await async_client.visuals.create_image(
            allow_nsfw=True,
            prompt="string",
        )
        assert visual.is_closed
        assert await visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_image_with_all_params(
        self, async_client: AsyncAlphakek, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        visual = await async_client.visuals.create_image(
            allow_nsfw=True,
            prompt="string",
            height=512,
            seed=0,
            width=512,
        )
        assert visual.is_closed
        assert await visual.json() == {"foo": "bar"}
        assert cast(Any, visual.is_closed) is True
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create_image(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        visual = await async_client.visuals.with_raw_response.create_image(
            allow_nsfw=True,
            prompt="string",
        )

        assert visual.is_closed is True
        assert visual.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await visual.json() == {"foo": "bar"}
        assert isinstance(visual, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create_image(self, async_client: AsyncAlphakek, respx_mock: MockRouter) -> None:
        respx_mock.post("/visuals/create_image").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.visuals.with_streaming_response.create_image(
            allow_nsfw=True,
            prompt="string",
        ) as visual:
            assert not visual.is_closed
            assert visual.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await visual.json() == {"foo": "bar"}
            assert cast(Any, visual.is_closed) is True
            assert isinstance(visual, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, visual.is_closed) is True
