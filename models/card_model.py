"""Mô hình dữ liệu của bảng cards."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True, slots=True)
class Card:
    """Đại diện cho một bản ghi trong bảng cards."""

    card_id: Optional[int] = None
    deck_id: int
    front_text: str
    back_text: str
    position: int
    is_deleted: bool = False
    created_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
