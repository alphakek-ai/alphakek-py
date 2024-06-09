# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._compat import cached_property
from .completion import (
    CompletionResource,
    AsyncCompletionResource,
    CompletionResourceWithRawResponse,
    AsyncCompletionResourceWithRawResponse,
    CompletionResourceWithStreamingResponse,
    AsyncCompletionResourceWithStreamingResponse,
)
from ..._resource import SyncAPIResource, AsyncAPIResource

__all__ = ["ChatResource", "AsyncChatResource"]


class ChatResource(SyncAPIResource):
    @cached_property
    def completion(self) -> CompletionResource:
        return CompletionResource(self._client)

    @cached_property
    def with_raw_response(self) -> ChatResourceWithRawResponse:
        return ChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ChatResourceWithStreamingResponse:
        return ChatResourceWithStreamingResponse(self)


class AsyncChatResource(AsyncAPIResource):
    @cached_property
    def completion(self) -> AsyncCompletionResource:
        return AsyncCompletionResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncChatResourceWithRawResponse:
        return AsyncChatResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncChatResourceWithStreamingResponse:
        return AsyncChatResourceWithStreamingResponse(self)


class ChatResourceWithRawResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

    @cached_property
    def completion(self) -> CompletionResourceWithRawResponse:
        return CompletionResourceWithRawResponse(self._chat.completion)


class AsyncChatResourceWithRawResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

    @cached_property
    def completion(self) -> AsyncCompletionResourceWithRawResponse:
        return AsyncCompletionResourceWithRawResponse(self._chat.completion)


class ChatResourceWithStreamingResponse:
    def __init__(self, chat: ChatResource) -> None:
        self._chat = chat

    @cached_property
    def completion(self) -> CompletionResourceWithStreamingResponse:
        return CompletionResourceWithStreamingResponse(self._chat.completion)


class AsyncChatResourceWithStreamingResponse:
    def __init__(self, chat: AsyncChatResource) -> None:
        self._chat = chat

    @cached_property
    def completion(self) -> AsyncCompletionResourceWithStreamingResponse:
        return AsyncCompletionResourceWithStreamingResponse(self._chat.completion)
