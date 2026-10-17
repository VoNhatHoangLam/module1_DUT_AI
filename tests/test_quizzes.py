"""Kiểm thử chức năng làm bài, nộp bài và xem lịch sử quiz."""

import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from models import Question, Quiz, QuizAnswer, QuizAttempt
from repositories import CsvRepository
from services import (
    AttemptAlreadySubmittedError,
    HistoryService,
    NoQuestionError,
    QuizService,
)
from utils import EmptyStackError, Stack


class StackTestCase(unittest.TestCase):
    def test_stack_uses_lifo_order(self) -> None:
        stack = Stack([1, 2, 3])

        self.assertEqual(stack.peek(), 3)
        self.assertEqual(stack.pop(), 3)
        self.assertEqual(stack.pop(), 2)
        self.assertEqual(stack.pop(), 1)
        self.assertTrue(stack.is_empty())
        with self.assertRaises(EmptyStackError):
            stack.pop()


class QuizServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        path = Path(self.temporary_directory.name)

        self.quiz_repo = self._repository(
            path / "quizzes.csv",
            Quiz,
            "quiz_id",
            "quiz_id,source_deck_id,title,description,time_limit_minutes,is_deleted,created_at,updated_at\n",
        )
        self.question_repo = self._repository(
            path / "questions.csv",
            Question,
            "question_id",
            "question_id,quiz_id,question_text,option_a,option_b,option_c,option_d,correct_answer,position,points,is_deleted\n",
            ("quiz_id",),
        )
        self.attempt_repo = self._repository(
            path / "quiz_attempts.csv",
            QuizAttempt,
            "attempt_id",
            "attempt_id,quiz_id,quiz_title_snapshot,attempt_status,started_at,submitted_at,total_questions,correct_count,score_percent\n",
            ("quiz_id",),
        )
        self.answer_repo = self._repository(
            path / "quiz_answers.csv",
            QuizAnswer,
            "answer_id",
            "answer_id,attempt_id,selected_answer,correct_answer_snapshot,is_correct,points_earned,question_text_snapshot,selected_option_text_snapshot,correct_option_text_snapshot\n",
            ("attempt_id",),
        )
        self.quiz_repo.add(Quiz(quiz_id=10, title="Quiz Python"))
        self.question_repo.add(
            Question(
                question_id=101,
                quiz_id=10,
                question_text="Kết quả của 1 + 1?",
                option_a="1",
                option_b="2",
                option_c="3",
                option_d="4",
                correct_answer="B",
                position=2,
                points=Decimal("2"),
            )
        )
        self.question_repo.add(
            Question(
                question_id=100,
                quiz_id=10,
                question_text="Python là gì?",
                option_a="Ngôn ngữ lập trình",
                option_b="Hệ điều hành",
                option_c="Cơ sở dữ liệu",
                option_d="Trình duyệt",
                correct_answer="A",
                position=1,
                points=Decimal("1"),
            )
        )
        self.service = QuizService(
            self.quiz_repo,
            self.question_repo,
            self.attempt_repo,
            self.answer_repo,
        )
        self.history = HistoryService(self.attempt_repo, self.answer_repo)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    @staticmethod
    def _repository(path, model, id_field, header, indexes=()):
        path.write_text(header, encoding="utf-8")
        return CsvRepository(path, model, id_field, indexes)

    def test_start_quiz_uses_stack_in_question_position_order(self) -> None:
        session = self.service.start_quiz(10)

        self.assertEqual(session.current_question.question_id, 100)
        session.answer_current("a")
        self.assertEqual(session.current_question.question_id, 101)
        self.assertEqual(session.selected_answers, {100: "A"})
        session.answer_current(None)
        self.assertTrue(session.is_completed)

    def test_submit_quiz_saves_score_and_answer_snapshots(self) -> None:
        session = self.service.start_quiz(10)
        session.answer_current("a")
        session.answer_current("d")

        result = self.service.submit_session(session)

        self.assertEqual(result.attempt.attempt_status, "SUBMITTED")
        self.assertEqual(result.attempt.correct_count, 1)
        self.assertEqual(result.attempt.total_questions, 2)
        self.assertEqual(result.attempt.score_percent, Decimal("33.33"))
        self.assertEqual(len(result.answers), 2)
        self.assertEqual(result.answers[0].selected_option_text_snapshot, "Ngôn ngữ lập trình")
        self.assertEqual(result.answers[1].correct_option_text_snapshot, "2")
        with self.assertRaises(AttemptAlreadySubmittedError):
            self.service.submit_session(session)

    def test_history_is_newest_first_and_result_is_found_by_attempt_id(self) -> None:
        first = self.service.start_quiz(10)
        first.answer_current("A")
        first.answer_current("B")
        submitted = self.service.submit_session(first)
        second = self.service.start_quiz(10)

        history = self.history.list_attempts()
        detail = self.history.get_attempt_result(submitted.attempt.attempt_id)

        self.assertEqual(history[0].attempt_id, second.attempt.attempt_id)
        self.assertEqual(detail.attempt.attempt_id, submitted.attempt.attempt_id)
        self.assertEqual(len(detail.answers), 2)
        self.assertEqual(
            [item.attempt_id for item in self.history.list_attempts(submitted_only=True)],
            [submitted.attempt.attempt_id],
        )

    def test_quiz_session_undo_and_redo_navigation(self) -> None:
        """Kiểm tra điều hướng tới và lui (Undo/Redo) giữa 3 câu hỏi bằng 2 Stack."""
        self.question_repo.add(
            Question(
                question_id=102,
                quiz_id=10,
                question_text="2 * 3 = ?",
                option_a="5",
                option_b="6",
                option_c="7",
                option_d="8",
                correct_answer="B",
                position=3,
                points=Decimal("1"),
            )
        )
        session = self.service.start_quiz(10)

        # 1. Bắt đầu tại Câu 100
        self.assertEqual(session.current_question.question_id, 100)
        self.assertFalse(session.can_undo)
        self.assertTrue(session.can_redo)
        self.assertIsNone(session.current_answer)
        self.assertEqual(session.remaining_count, 3)

        # 2. Trả lời Câu 100 -> Tiến sang Câu 101
        ans_q100 = session.answer_current("a")
        self.assertEqual(ans_q100.question_id, 100)
        self.assertEqual(session.current_question.question_id, 101)
        self.assertTrue(session.can_undo)
        self.assertTrue(session.can_redo)
        self.assertEqual(session.remaining_count, 2)

        # 3. Trả lời Câu 101 -> Tiến sang Câu 102
        ans_q101 = session.answer_current("b")
        self.assertEqual(ans_q101.question_id, 101)
        self.assertEqual(session.current_question.question_id, 102)
        self.assertTrue(session.can_undo)
        self.assertFalse(session.can_redo)
        self.assertEqual(session.remaining_count, 1)

        # 4. UNDO lần 1: Từ Câu 102 quay lại Câu 101
        prev_q = session.undo()
        self.assertEqual(prev_q.question_id, 101)
        self.assertEqual(session.current_question.question_id, 101)
        self.assertEqual(session.current_answer, "B")
        self.assertTrue(session.can_undo)
        self.assertTrue(session.can_redo)

        # 5. UNDO lần 2: Từ Câu 101 quay lại Câu 100
        prev_q2 = session.undo()
        self.assertEqual(prev_q2.question_id, 100)
        self.assertEqual(session.current_question.question_id, 100)
        self.assertEqual(session.current_answer, "A")
        self.assertFalse(session.can_undo)  # Đã ở câu đầu tiên
        self.assertTrue(session.can_redo)

        # 6. REDO lần 1: Từ Câu 100 tiến lại Câu 101
        next_q = session.redo()
        self.assertEqual(next_q.question_id, 101)
        self.assertEqual(session.current_question.question_id, 101)
        self.assertEqual(session.current_answer, "B")
        self.assertTrue(session.can_undo)
        self.assertTrue(session.can_redo)

        # 7. REDO lần 2: Từ Câu 101 tiến lại Câu 102
        next_q2 = session.redo()
        self.assertEqual(next_q2.question_id, 102)
        self.assertEqual(session.current_question.question_id, 102)
        self.assertTrue(session.can_undo)
        self.assertFalse(session.can_redo)

        # 8. Trả lời Câu 102 và hoàn tất bài thi
        session.answer_current("b")
        self.assertTrue(session.is_completed)
        self.assertIsNone(session.current_question)
        self.assertEqual(
            session.selected_answers,
            {100: "A", 101: "B", 102: "B"},
        )

        # 9. Sau khi hoàn thành, vẫn có thể UNDO để xem lại câu cuối trước khi nộp
        last_q = session.undo()
        self.assertEqual(last_q.question_id, 102)
        self.assertFalse(session.is_completed)
        self.assertEqual(session.current_answer, "B")

    def test_quiz_session_change_answer_after_undo(self) -> None:
        """Kiểm tra thay đổi đáp án sau khi Undo."""
        session = self.service.start_quiz(10)

        # Trả lời câu 100 là A
        session.answer_current("a")
        self.assertEqual(session.current_question.question_id, 101)

        # Undo về câu 100 và đổi đáp án thành D
        session.undo()
        self.assertEqual(session.current_question.question_id, 100)
        self.assertEqual(session.current_answer, "A")

        session.answer_current("d")
        self.assertEqual(session.selected_answers[100], "D")

        # Trả lời câu 101 là B
        self.assertEqual(session.current_question.question_id, 101)
        session.answer_current("b")
        self.assertTrue(session.is_completed)

        # Nộp bài và xác nhận điểm số phản ánh đáp án mới
        result = self.service.submit_session(session)
        self.assertEqual(result.attempt.correct_count, 1)  # 100 sai (D!=A), 101 đúng (B==B)

    def test_quiz_session_undo_at_first_question_raises_error(self) -> None:
        """Bấm Undo khi đang ở câu đầu tiên ném ngoại lệ NoQuestionError."""
        session = self.service.start_quiz(10)
        self.assertFalse(session.can_undo)
        with self.assertRaises(NoQuestionError):
            session.undo()

    def test_quiz_session_redo_when_empty_raises_error(self) -> None:
        """Bấm Redo khi không có câu phía trước ném ngoại lệ NoQuestionError."""
        session = self.service.start_quiz(10)
        session.answer_current("a")
        session.answer_current("b")
        # Đã ở câu cuối cùng và hoàn thành, không có câu nào phía trước để redo
        self.assertFalse(session.can_redo)
        with self.assertRaises(NoQuestionError):
            session.redo()


if __name__ == "__main__":
    unittest.main()

