# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["User", "Dialogs", "DialogsMessage", "Bonus"]


class DialogsMessage(BaseModel):
    author: Literal["USER", "ASSISTANT", "SYSTEM"]
    """Message author"""

    text: str


class Dialogs(BaseModel):
    dialog_id: str
    """Dialog ID"""

    messages: List[DialogsMessage]

    title: Optional[str] = None
    """Dialog title"""

    last_time_updated: Optional[datetime] = None
    """Last time dialog was updated"""


class Bonus(BaseModel):
    description: str

    usd_value: float


class User(BaseModel):
    address: str
    """User's Ethereum address in lowercase"""

    credits: float

    dialogs: Dict[str, Dialogs]
    """List of user's dialogs' IDs"""

    bonuses: Optional[List[Bonus]] = None
    """List of user's bonuses"""

    max_dialogs: Optional[int] = None
    """Maximum number of dialogs per user"""

    telegram_id: Optional[int] = None
    """User's Telegram ID"""

    tier: Optional[Literal["BASIC", "HODLER", "PREMIUM", "ELITE", "DEVELOPER"]] = None
    """User tier"""

    tokens: Optional[float] = None
    """User's tokens balance"""

    tokens_usd: Optional[float] = None
    """User's tokens balance in USD"""
