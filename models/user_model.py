"""Mô hình dữ liệu của bảng users."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(kw_only=True, slots=True)
class User:
    """Đại diện cho một bản ghi trong bảng users."""

    user_id: Optional[int] = None
    username: str
    password_hash: str
    role: str = "USER"
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    account_status: str = "ACTIVE"
    created_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
    updated_at: datetime = field(
        default_factory=lambda: datetime.now().replace(microsecond=0)
    )
    last_login_at: Optional[datetime] = None
