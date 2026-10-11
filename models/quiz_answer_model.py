"""Mô hình dữ liệu của bảng quiz_answers."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(kw_only=True, slots=True)
class QuizAnswer:
    """Đại diện cho một bản ghi trong bảng quiz_answers."""

    answer_id: Optional[int] = None
    attempt_id: int
    question_id: int
    selected_answer: Optional[str] = None
    correct_answer_snapshot: str
    is_correct: bool
    points_earned: Decimal = Decimal("0")
    question_text_snapshot: str
    selected_option_text_snapshot: Optional[str] = None
    correct_option_text_snapshot: str
    answered_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
