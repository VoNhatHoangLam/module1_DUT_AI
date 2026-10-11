"""Mô hình dữ liệu của bảng account_status_logs."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True, slots=True)
class AccountStatusLog:
    """Đại diện cho một bản ghi trong bảng account_status_logs."""

    status_change_id: Optional[int] = None
    target_user_id: int
    admin_id: int
    old_status: str
    new_status: str
    reason: Optional[str] = None
    changed_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
