# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["VisualCreateImageParams"]


class VisualCreateImageParams(TypedDict, total=False):
    allow_nsfw: Required[bool]

    prompt: Required[str]

    height: int

    seed: int

    width: int
