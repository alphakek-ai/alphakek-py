# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Literal, Required, TypedDict

__all__ = ["KnowledgeSearchParams"]


class KnowledgeSearchParams(TypedDict, total=False):
    query: Required[str]

    count: int

    offset: int

    sort_by: Literal["relevance", "date"]

    sources: List[Literal["news", "4chan"]]
