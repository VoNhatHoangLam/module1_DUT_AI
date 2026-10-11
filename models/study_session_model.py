"""Mô hình dữ liệu của bảng study_sessions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True, slots=True)
class StudySession:
    """Đại diện cho một bản ghi trong bảng study_sessions."""

    study_session_id: Optional[int] = None
    user_id: int
    deck_id: int
    started_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
    ended_at: Optional[datetime] = None
