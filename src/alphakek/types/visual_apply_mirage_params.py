# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .._types import FileTypes

__all__ = ["VisualApplyMirageParams"]


class VisualApplyMirageParams(TypedDict, total=False):
    image: Required[FileTypes]

    prompt: Required[str]

    allow_nsfw: bool

    seed: int
