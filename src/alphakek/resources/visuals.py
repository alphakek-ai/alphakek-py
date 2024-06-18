# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ..types import visual_apply_effect_params, visual_apply_mirage_params, visual_create_image_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from .._utils import (
    extract_files,
    maybe_transform,
    deepcopy_minimal,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_custom_raw_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import (
    make_request_options,
)

__all__ = ["VisualsResource", "AsyncVisualsResource"]


class VisualsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> VisualsResourceWithRawResponse:
        return VisualsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> VisualsResourceWithStreamingResponse:
        return VisualsResourceWithStreamingResponse(self)

    def apply_effect(
        self,
        *,
        image: FileTypes,
        prompt: str,
        allow_nsfw: bool | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Apply an effect to an image

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "allow_nsfw": allow_nsfw,
                "seed": seed,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/visuals/apply_effect",
            body=maybe_transform(body, visual_apply_effect_params.VisualApplyEffectParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def apply_mirage(
        self,
        *,
        image: FileTypes,
        prompt: str,
        allow_nsfw: bool | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Apply a mirage effect to an image

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "allow_nsfw": allow_nsfw,
                "seed": seed,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/visuals/apply_mirage",
            body=maybe_transform(body, visual_apply_mirage_params.VisualApplyMirageParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def create_image(
        self,
        *,
        allow_nsfw: bool,
        prompt: str,
        height: int | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Create an image from a text prompt

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        return self._post(
            "/visuals/create_image",
            body=maybe_transform(
                {
                    "allow_nsfw": allow_nsfw,
                    "prompt": prompt,
                    "height": height,
                    "seed": seed,
                    "width": width,
                },
                visual_create_image_params.VisualCreateImageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncVisualsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncVisualsResourceWithRawResponse:
        return AsyncVisualsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncVisualsResourceWithStreamingResponse:
        return AsyncVisualsResourceWithStreamingResponse(self)

    async def apply_effect(
        self,
        *,
        image: FileTypes,
        prompt: str,
        allow_nsfw: bool | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Apply an effect to an image

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "allow_nsfw": allow_nsfw,
                "seed": seed,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/visuals/apply_effect",
            body=await async_maybe_transform(body, visual_apply_effect_params.VisualApplyEffectParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def apply_mirage(
        self,
        *,
        image: FileTypes,
        prompt: str,
        allow_nsfw: bool | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Apply a mirage effect to an image

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        body = deepcopy_minimal(
            {
                "image": image,
                "prompt": prompt,
                "allow_nsfw": allow_nsfw,
                "seed": seed,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["image"]])
        if files:
            # It should be noted that the actual Content-Type header that will be
            # sent to the server will contain a `boundary` parameter, e.g.
            # multipart/form-data; boundary=---abc--
            extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/visuals/apply_mirage",
            body=await async_maybe_transform(body, visual_apply_mirage_params.VisualApplyMirageParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def create_image(
        self,
        *,
        allow_nsfw: bool,
        prompt: str,
        height: int | NotGiven = NOT_GIVEN,
        seed: int | NotGiven = NOT_GIVEN,
        width: int | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Create an image from a text prompt

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "image/png", **(extra_headers or {})}
        return await self._post(
            "/visuals/create_image",
            body=await async_maybe_transform(
                {
                    "allow_nsfw": allow_nsfw,
                    "prompt": prompt,
                    "height": height,
                    "seed": seed,
                    "width": width,
                },
                visual_create_image_params.VisualCreateImageParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class VisualsResourceWithRawResponse:
    def __init__(self, visuals: VisualsResource) -> None:
        self._visuals = visuals

        self.apply_effect = to_custom_raw_response_wrapper(
            visuals.apply_effect,
            BinaryAPIResponse,
        )
        self.apply_mirage = to_custom_raw_response_wrapper(
            visuals.apply_mirage,
            BinaryAPIResponse,
        )
        self.create_image = to_custom_raw_response_wrapper(
            visuals.create_image,
            BinaryAPIResponse,
        )


class AsyncVisualsResourceWithRawResponse:
    def __init__(self, visuals: AsyncVisualsResource) -> None:
        self._visuals = visuals

        self.apply_effect = async_to_custom_raw_response_wrapper(
            visuals.apply_effect,
            AsyncBinaryAPIResponse,
        )
        self.apply_mirage = async_to_custom_raw_response_wrapper(
            visuals.apply_mirage,
            AsyncBinaryAPIResponse,
        )
        self.create_image = async_to_custom_raw_response_wrapper(
            visuals.create_image,
            AsyncBinaryAPIResponse,
        )


class VisualsResourceWithStreamingResponse:
    def __init__(self, visuals: VisualsResource) -> None:
        self._visuals = visuals

        self.apply_effect = to_custom_streamed_response_wrapper(
            visuals.apply_effect,
            StreamedBinaryAPIResponse,
        )
        self.apply_mirage = to_custom_streamed_response_wrapper(
            visuals.apply_mirage,
            StreamedBinaryAPIResponse,
        )
        self.create_image = to_custom_streamed_response_wrapper(
            visuals.create_image,
            StreamedBinaryAPIResponse,
        )


class AsyncVisualsResourceWithStreamingResponse:
    def __init__(self, visuals: AsyncVisualsResource) -> None:
        self._visuals = visuals

        self.apply_effect = async_to_custom_streamed_response_wrapper(
            visuals.apply_effect,
            AsyncStreamedBinaryAPIResponse,
        )
        self.apply_mirage = async_to_custom_streamed_response_wrapper(
            visuals.apply_mirage,
            AsyncStreamedBinaryAPIResponse,
        )
        self.create_image = async_to_custom_streamed_response_wrapper(
            visuals.create_image,
            AsyncStreamedBinaryAPIResponse,
        )
