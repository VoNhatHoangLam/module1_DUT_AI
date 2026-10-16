"""Nghiệp vụ tra cứu lịch sử và kết quả làm quiz."""

from __future__ import annotations

from typing import Optional

from config import DATA_DIR
from models import QuizAnswer, QuizAttempt
from repositories import CsvRepository
from .quiz_service import AttemptNotFoundError, QuizAttemptResult


class HistoryService:
    """Đọc danh sách lượt thi và chi tiết của từng attempt_id."""

    def __init__(
        self,
        attempt_repository: Optional[CsvRepository[QuizAttempt]] = None,
        answer_repository: Optional[CsvRepository[QuizAnswer]] = None,
    ) -> None:
        self.attempt_repository = attempt_repository or CsvRepository(
            DATA_DIR / "quiz_attempts.csv", QuizAttempt, "attempt_id", ("quiz_id",)
        )
        self.answer_repository = answer_repository or CsvRepository(
            DATA_DIR / "quiz_answers.csv", QuizAnswer, "answer_id", ("attempt_id",)
        )

    def list_attempts(
        self, quiz_id: Optional[int] = None, *, submitted_only: bool = False
    ) -> list[QuizAttempt]:
        attempts = (
            self.attempt_repository.find_by(quiz_id=quiz_id)
            if quiz_id is not None
            else self.attempt_repository.get_all()
        )
        if submitted_only:
            attempts = [
                item
                for item in attempts
                if item.attempt_status in {"SUBMITTED", "COMPLETED"}
                or item.submitted_at is not None
            ]
        return sorted(
            attempts,
            key=lambda item: (item.submitted_at or item.started_at, item.attempt_id or 0),
            reverse=True,
        )

    def get_attempt_result(self, attempt_id: int) -> QuizAttemptResult:
        attempt = self.attempt_repository.get_by_id(attempt_id)
        if attempt is None:
            raise AttemptNotFoundError(f"Không tìm thấy attempt_id={attempt_id}")
        answers = sorted(
            self.answer_repository.find_by(attempt_id=attempt_id),
            key=lambda item: item.answer_id or 0,
        )
        return QuizAttemptResult(attempt=attempt, answers=tuple(answers))

    # Tên ngắn gọn tương thích với cách gọi phổ biến ở tầng giao diện.
    get_result = get_attempt_result
    get_history = list_attempts
