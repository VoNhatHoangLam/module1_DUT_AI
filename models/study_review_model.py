"""Mô hình dữ liệu của bảng study_reviews."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True, slots=True)
class StudyReview:
    """Đại diện cho một bản ghi trong bảng study_reviews."""

    study_review_id: Optional[int] = None
    study_session_id: int
    card_id: int
    result: str
    reviewed_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
