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


if __name__ == "__main__":
    unittest.main()
