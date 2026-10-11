"""Mô hình dữ liệu của bảng quiz_attempts."""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(kw_only=True, slots=True)
class QuizAttempt:
    """Đại diện cho một bản ghi trong bảng quiz_attempts."""

    attempt_id: Optional[int] = None
    quiz_id: int
    user_id: int
    quiz_title_snapshot: str
    attempt_status: str = "STARTED"
    started_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
    submitted_at: Optional[datetime] = None
    total_questions: Optional[int] = None
    correct_count: Optional[int] = None
    score_percent: Optional[Decimal] = None
