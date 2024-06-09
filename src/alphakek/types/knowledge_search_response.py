# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .knowledge_document_view import KnowledgeDocumentView

__all__ = ["KnowledgeSearchResponse"]


class KnowledgeSearchResponse(BaseModel):
    documents: List[KnowledgeDocumentView]

    total_found: int

    count: Optional[int] = None

    offset: Optional[int] = None
