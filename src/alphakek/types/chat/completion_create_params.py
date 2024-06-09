# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

__all__ = ["CompletionCreateParams", "Message"]


class CompletionCreateParams(TypedDict, total=False):
    messages: Required[Iterable[Message]]

    model: Required[Literal["versa", "nexus", "eclipse"]]

    persona: Optional[str]

    stream: bool


class MessageTyped(TypedDict, total=False):
    content: Required[str]

    role: Required[Literal["system", "user", "assistant"]]


Message = Union[MessageTyped, Dict[str, object]]
