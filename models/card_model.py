"""Mô hình dữ liệu của bảng cards."""

from dataclasses import dataclass
from typing import Optional


@dataclass(kw_only=True, slots=True)
class Card:
    """Đại diện cho một bản ghi trong bảng cards."""

    card_id: Optional[int] = None
    deck_id: int
    front_text: str
    back_text: str
    position: int
