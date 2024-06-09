# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal

import httpx

from ..types import knowledge_search_params, knowledge_get_by_link_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import (
    maybe_transform,
    async_maybe_transform,
)
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import (
    make_request_options,
)
from ..types.knowledge_document_view import KnowledgeDocumentView
from ..types.knowledge_search_response import KnowledgeSearchResponse

__all__ = ["KnowledgeResource", "AsyncKnowledgeResource"]


class KnowledgeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> KnowledgeResourceWithRawResponse:
        return KnowledgeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> KnowledgeResourceWithStreamingResponse:
        return KnowledgeResourceWithStreamingResponse(self)

    def get_by_link(
        self,
        *,
        link: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeDocumentView:
        """
        Get knowledge by link

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/knowledge/get/by_link",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"link": link}, knowledge_get_by_link_params.KnowledgeGetByLinkParams),
            ),
            cast_to=KnowledgeDocumentView,
        )

    def search(
        self,
        *,
        query: str,
        count: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["relevance", "date"] | NotGiven = NOT_GIVEN,
        sources: List[Literal["news", "4chan"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeSearchResponse:
        """
        Search knowledge documents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/knowledge/search",
            body=maybe_transform(
                {
                    "query": query,
                    "count": count,
                    "offset": offset,
                    "sort_by": sort_by,
                    "sources": sources,
                },
                knowledge_search_params.KnowledgeSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeSearchResponse,
        )


class AsyncKnowledgeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncKnowledgeResourceWithRawResponse:
        return AsyncKnowledgeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncKnowledgeResourceWithStreamingResponse:
        return AsyncKnowledgeResourceWithStreamingResponse(self)

    async def get_by_link(
        self,
        *,
        link: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeDocumentView:
        """
        Get knowledge by link

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/knowledge/get/by_link",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"link": link}, knowledge_get_by_link_params.KnowledgeGetByLinkParams
                ),
            ),
            cast_to=KnowledgeDocumentView,
        )

    async def search(
        self,
        *,
        query: str,
        count: int | NotGiven = NOT_GIVEN,
        offset: int | NotGiven = NOT_GIVEN,
        sort_by: Literal["relevance", "date"] | NotGiven = NOT_GIVEN,
        sources: List[Literal["news", "4chan"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> KnowledgeSearchResponse:
        """
        Search knowledge documents

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/knowledge/search",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "count": count,
                    "offset": offset,
                    "sort_by": sort_by,
                    "sources": sources,
                },
                knowledge_search_params.KnowledgeSearchParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=KnowledgeSearchResponse,
        )


class KnowledgeResourceWithRawResponse:
    def __init__(self, knowledge: KnowledgeResource) -> None:
        self._knowledge = knowledge

        self.get_by_link = to_raw_response_wrapper(
            knowledge.get_by_link,
        )
        self.search = to_raw_response_wrapper(
            knowledge.search,
        )


class AsyncKnowledgeResourceWithRawResponse:
    def __init__(self, knowledge: AsyncKnowledgeResource) -> None:
        self._knowledge = knowledge

        self.get_by_link = async_to_raw_response_wrapper(
            knowledge.get_by_link,
        )
        self.search = async_to_raw_response_wrapper(
            knowledge.search,
        )


class KnowledgeResourceWithStreamingResponse:
    def __init__(self, knowledge: KnowledgeResource) -> None:
        self._knowledge = knowledge

        self.get_by_link = to_streamed_response_wrapper(
            knowledge.get_by_link,
        )
        self.search = to_streamed_response_wrapper(
            knowledge.search,
        )


class AsyncKnowledgeResourceWithStreamingResponse:
    def __init__(self, knowledge: AsyncKnowledgeResource) -> None:
        self._knowledge = knowledge

        self.get_by_link = async_to_streamed_response_wrapper(
            knowledge.get_by_link,
        )
        self.search = async_to_streamed_response_wrapper(
            knowledge.search,
        )
