"""Mô hình dữ liệu của bảng decks."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True, slots=True)
class Deck:
    """Đại diện cho một bản ghi trong bảng decks."""

    deck_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    total_cards: int = 0
    is_studied: bool = False
    is_deleted: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
