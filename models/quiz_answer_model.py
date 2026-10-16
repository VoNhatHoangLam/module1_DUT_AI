"""Mô hình dữ liệu của bảng quiz_answers."""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(kw_only=True, slots=True)
class QuizAnswer:
    """Đại diện cho một bản ghi trong bảng quiz_answers."""

    answer_id: Optional[int] = None
    attempt_id: int
    selected_answer: Optional[str] = None
    correct_answer_snapshot: str
    is_correct: bool
    points_earned: Decimal = Decimal("0")
    question_text_snapshot: str
    selected_option_text_snapshot: Optional[str] = None
    correct_option_text_snapshot: str
