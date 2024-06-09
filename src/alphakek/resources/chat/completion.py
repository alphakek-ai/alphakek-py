# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import (
    maybe_transform,
    async_maybe_transform,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.chat import completion_create_params
from ..._base_client import (
    make_request_options,
)
from ...types.chat.chat_completion import ChatCompletion

__all__ = ["CompletionResource", "AsyncCompletionResource"]


class CompletionResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CompletionResourceWithRawResponse:
        return CompletionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CompletionResourceWithStreamingResponse:
        return CompletionResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: Literal["versa", "nexus", "eclipse"],
        persona: Optional[str] | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion:
        """
        Chat Completions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/chat/completions",
            body=maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "persona": persona,
                    "stream": stream,
                },
                completion_create_params.CompletionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatCompletion,
        )


class AsyncCompletionResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCompletionResourceWithRawResponse:
        return AsyncCompletionResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCompletionResourceWithStreamingResponse:
        return AsyncCompletionResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        messages: Iterable[completion_create_params.Message],
        model: Literal["versa", "nexus", "eclipse"],
        persona: Optional[str] | NotGiven = NOT_GIVEN,
        stream: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ChatCompletion:
        """
        Chat Completions

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/chat/completions",
            body=await async_maybe_transform(
                {
                    "messages": messages,
                    "model": model,
                    "persona": persona,
                    "stream": stream,
                },
                completion_create_params.CompletionCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ChatCompletion,
        )


class CompletionResourceWithRawResponse:
    def __init__(self, completion: CompletionResource) -> None:
        self._completion = completion

        self.create = to_raw_response_wrapper(
            completion.create,
        )


class AsyncCompletionResourceWithRawResponse:
    def __init__(self, completion: AsyncCompletionResource) -> None:
        self._completion = completion

        self.create = async_to_raw_response_wrapper(
            completion.create,
        )


class CompletionResourceWithStreamingResponse:
    def __init__(self, completion: CompletionResource) -> None:
        self._completion = completion

        self.create = to_streamed_response_wrapper(
            completion.create,
        )


class AsyncCompletionResourceWithStreamingResponse:
    def __init__(self, completion: AsyncCompletionResource) -> None:
        self._completion = completion

        self.create = async_to_streamed_response_wrapper(
            completion.create,
        )
