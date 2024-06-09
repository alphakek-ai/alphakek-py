# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["KnowledgeDocumentView"]


class KnowledgeDocumentView(BaseModel):
    last_time_updated: datetime

    source: str

    title: str

    bullishness: Optional[float] = None

    legitimacy: Optional[float] = None

    summary: Optional[str] = None

    tldr: Optional[str] = None
