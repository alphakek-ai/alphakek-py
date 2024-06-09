# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

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
from ..._base_client import (
    make_request_options,
)
from ...types.knowledge import get_by_link_params
from ...types.knowledge_document_view import KnowledgeDocumentView

__all__ = ["GetResource", "AsyncGetResource"]


class GetResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> GetResourceWithRawResponse:
        return GetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> GetResourceWithStreamingResponse:
        return GetResourceWithStreamingResponse(self)

    def by_link(
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
                query=maybe_transform({"link": link}, get_by_link_params.GetByLinkParams),
            ),
            cast_to=KnowledgeDocumentView,
        )


class AsyncGetResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncGetResourceWithRawResponse:
        return AsyncGetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncGetResourceWithStreamingResponse:
        return AsyncGetResourceWithStreamingResponse(self)

    async def by_link(
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
                query=await async_maybe_transform({"link": link}, get_by_link_params.GetByLinkParams),
            ),
            cast_to=KnowledgeDocumentView,
        )


class GetResourceWithRawResponse:
    def __init__(self, get: GetResource) -> None:
        self._get = get

        self.by_link = to_raw_response_wrapper(
            get.by_link,
        )


class AsyncGetResourceWithRawResponse:
    def __init__(self, get: AsyncGetResource) -> None:
        self._get = get

        self.by_link = async_to_raw_response_wrapper(
            get.by_link,
        )


class GetResourceWithStreamingResponse:
    def __init__(self, get: GetResource) -> None:
        self._get = get

        self.by_link = to_streamed_response_wrapper(
            get.by_link,
        )


class AsyncGetResourceWithStreamingResponse:
    def __init__(self, get: AsyncGetResource) -> None:
        self._get = get

        self.by_link = async_to_streamed_response_wrapper(
            get.by_link,
        )
