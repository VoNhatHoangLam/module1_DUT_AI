"""Nghiệp vụ làm và nộp bài quiz."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Mapping, Optional

from config import DATA_DIR
from models import Question, Quiz, QuizAnswer, QuizAttempt
from repositories import CsvRepository
from utils import Stack


class QuizNotFoundError(LookupError):
    """Không tìm thấy quiz có thể làm."""


class AttemptNotFoundError(LookupError):
    """Không tìm thấy lượt làm bài."""


class AttemptAlreadySubmittedError(ValueError):
    """Lượt làm bài đã được nộp trước đó."""


class NoQuestionError(ValueError):
    """Quiz không có câu hỏi để làm."""


@dataclass(frozen=True, slots=True)
class QuizAttemptResult:
    """Kết quả tổng quát và chi tiết đáp án của một lượt làm bài."""

    attempt: QuizAttempt
    answers: tuple[QuizAnswer, ...]


class QuizSession:
    """Phiên làm bài tuần tự; câu chưa làm được quản lý bằng Stack."""

    def __init__(self, attempt: QuizAttempt, questions: list[Question]) -> None:
        self.attempt = attempt
        self._questions: Stack[Question] = Stack()
        # Stack là LIFO, do đó đẩy theo thứ tự ngược để câu position nhỏ nhất ở đỉnh.
        for question in reversed(sorted(questions, key=lambda item: item.position)):
            self._questions.push(question)
        self._selected_answers: dict[int, Optional[str]] = {}

    @property
    def current_question(self) -> Optional[Question]:
        return None if self._questions.is_empty() else self._questions.peek()

    @property
    def remaining_count(self) -> int:
        return len(self._questions)

    @property
    def is_completed(self) -> bool:
        return self._questions.is_empty()

    @property
    def selected_answers(self) -> dict[int, Optional[str]]:
        return dict(self._selected_answers)

    def answer_current(self, selected_answer: Optional[str]) -> Question:
        """Ghi nhận lựa chọn rồi lấy câu hiện tại khỏi Stack."""

        if self._questions.is_empty():
            raise NoQuestionError("Phiên làm bài không còn câu hỏi")
        normalized = QuizService.normalize_answer(selected_answer)
        question = self._questions.pop()
        assert question.question_id is not None
        self._selected_answers[question.question_id] = normalized
        return question


class QuizService:
    """Khởi tạo phiên quiz, chấm điểm và lưu kết quả."""

    def __init__(
        self,
        quiz_repository: Optional[CsvRepository[Quiz]] = None,
        question_repository: Optional[CsvRepository[Question]] = None,
        attempt_repository: Optional[CsvRepository[QuizAttempt]] = None,
        answer_repository: Optional[CsvRepository[QuizAnswer]] = None,
    ) -> None:
        self.quiz_repository = quiz_repository or CsvRepository(
            DATA_DIR / "quizzes.csv", Quiz, "quiz_id"
        )
        self.question_repository = question_repository or CsvRepository(
            DATA_DIR / "questions.csv", Question, "question_id", ("quiz_id",)
        )
        self.attempt_repository = attempt_repository or CsvRepository(
            DATA_DIR / "quiz_attempts.csv", QuizAttempt, "attempt_id", ("quiz_id",)
        )
        self.answer_repository = answer_repository or CsvRepository(
            DATA_DIR / "quiz_answers.csv", QuizAnswer, "answer_id", ("attempt_id",)
        )

    def start_quiz(self, quiz_id: int) -> QuizSession:
        quiz = self.quiz_repository.get_by_id(quiz_id)
        if quiz is None or quiz.is_deleted:
            raise QuizNotFoundError(f"Không tìm thấy quiz_id={quiz_id}")

        questions = sorted(
            (
                question
                for question in self.question_repository.find_by(quiz_id=quiz_id)
                if not question.is_deleted
            ),
            key=lambda item: item.position,
        )
        if not questions:
            raise NoQuestionError("Quiz không có câu hỏi để làm")

        attempt = self.attempt_repository.add(
            QuizAttempt(
                quiz_id=quiz_id,
                quiz_title_snapshot=quiz.title,
                total_questions=len(questions),
            )
        )
        return QuizSession(attempt, questions)

    def submit_quiz(
        self,
        attempt_id: int,
        selected_answers: Mapping[int, Optional[str]],
    ) -> QuizAttemptResult:
        attempt = self.attempt_repository.get_by_id(attempt_id)
        if attempt is None:
            raise AttemptNotFoundError(f"Không tìm thấy attempt_id={attempt_id}")
        if attempt.attempt_status != "STARTED" or attempt.submitted_at is not None:
            raise AttemptAlreadySubmittedError(f"attempt_id={attempt_id} đã được nộp")

        questions = sorted(
            (
                question
                for question in self.question_repository.find_by(quiz_id=attempt.quiz_id)
                if not question.is_deleted
            ),
            key=lambda item: item.position,
        )
        if not questions:
            raise NoQuestionError("Quiz không có câu hỏi để chấm")

        question_ids = {question.question_id for question in questions}
        unknown_ids = set(selected_answers) - question_ids
        if unknown_ids:
            raise ValueError(f"Câu hỏi không thuộc quiz: {sorted(unknown_ids)}")

        normalized_answers = {
            question_id: self.normalize_answer(answer)
            for question_id, answer in selected_answers.items()
        }
        answer_records: list[QuizAnswer] = []
        earned_points = Decimal("0")
        total_points = Decimal("0")
        correct_count = 0

        for question in questions:
            selected = normalized_answers.get(question.question_id)
            correct_answer = self.normalize_answer(question.correct_answer)
            assert correct_answer is not None
            is_correct = selected == correct_answer
            points = question.points if question.points > 0 else Decimal("0")
            total_points += points
            if is_correct:
                correct_count += 1
                earned_points += points
            answer_records.append(
                QuizAnswer(
                    attempt_id=attempt_id,
                    selected_answer=selected,
                    correct_answer_snapshot=correct_answer,
                    is_correct=is_correct,
                    points_earned=points if is_correct else Decimal("0"),
                    question_text_snapshot=question.question_text,
                    selected_option_text_snapshot=(
                        self._option_text(question, selected) if selected else None
                    ),
                    correct_option_text_snapshot=self._option_text(
                        question, correct_answer
                    ),
                )
            )

        # Ghi chi tiết trước; chỉ chuyển attempt sang SUBMITTED khi chi tiết đã lưu đủ.
        saved_answers = tuple(
            self.answer_repository.add(answer) for answer in answer_records
        )
        attempt.attempt_status = "SUBMITTED"
        attempt.submitted_at = datetime.now().replace(microsecond=0)
        attempt.total_questions = len(questions)
        attempt.correct_count = correct_count
        attempt.score_percent = (
            (earned_points * Decimal("100") / total_points).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            if total_points > 0
            else Decimal("0.00")
        )
        self.attempt_repository.update(attempt)
        return QuizAttemptResult(attempt=attempt, answers=saved_answers)

    def submit_session(self, session: QuizSession) -> QuizAttemptResult:
        if session.attempt.attempt_id is None:
            raise AttemptNotFoundError("Phiên làm bài chưa có attempt_id")
        return self.submit_quiz(session.attempt.attempt_id, session.selected_answers)

    @staticmethod
    def normalize_answer(selected_answer: Optional[str]) -> Optional[str]:
        if selected_answer is None:
            return None
        if not isinstance(selected_answer, str):
            raise TypeError("Đáp án phải là chuỗi A, B, C, D hoặc None")
        normalized = selected_answer.strip().upper()
        if normalized not in {"A", "B", "C", "D"}:
            raise ValueError("Đáp án phải là A, B, C hoặc D")
        return normalized

    @staticmethod
    def _option_text(question: Question, answer: str) -> str:
        normalized = answer.strip().upper()
        try:
            return {
                "A": question.option_a,
                "B": question.option_b,
                "C": question.option_c,
                "D": question.option_d,
            }[normalized]
        except KeyError as error:
            raise ValueError("Đáp án đúng của câu hỏi phải là A, B, C hoặc D") from error
