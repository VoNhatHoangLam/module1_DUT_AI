"""Mô hình dữ liệu của bảng questions."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(kw_only=True, slots=True)
class Question:
    """Đại diện cho một bản ghi trong bảng questions."""

    question_id: Optional[int] = None
    quiz_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str
    position: int
    points: Decimal = Decimal("1")
    is_deleted: bool = False
