"""Kiểm thử tích hợp End-to-End giữa FastAPI và các Service nghiệp vụ."""

import unittest
from fastapi.testclient import TestClient

from main import app


class ApiIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_01_get_decks_list(self) -> None:
        response = self.client.get("/api/decks")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total_pages", data)
        self.assertIsInstance(data["items"], list)

    def test_02_create_and_delete_deck(self) -> None:
        payload = {
            "title": "Bộ thẻ Test API Integration",
            "description": "Mô tả kiểm thử",
            "category": "Test",
            "privacy": "public",
            "cards": [
                {"term": "CPU", "definition": "Central Processing Unit", "position": 1},
                {"term": "RAM", "definition": "Random Access Memory", "position": 2},
            ],
        }
        create_res = self.client.post("/api/decks", json=payload)
        self.assertEqual(create_res.status_code, 200)
        created = create_res.json()
        deck_id = created.get("deck_id") or int(created["id"])
        self.assertTrue(deck_id > 0)

        # Bắt đầu phiên học flashcard với bộ thẻ vừa tạo (Queue FIFO test)
        study_start = self.client.post("/api/study/start", json={"deck_id": deck_id})
        self.assertEqual(study_start.status_code, 200)
        session_data = study_start.json()
        self.assertIn("session_id", session_data)
        self.assertEqual(session_data["total_cards"], 2)
        session_id = session_data["session_id"]

        # Đánh dấu thẻ 1 chưa thuộc -> thẻ phải được enqueue vào cuối queue
        mark_res1 = self.client.post(f"/api/study/{session_id}/mark", json={"is_known": False})
        self.assertEqual(mark_res1.status_code, 200)
        state1 = mark_res1.json()
        self.assertEqual(state1["unknown_count"], 1)

        # Xóa bộ thẻ test
        del_res = self.client.delete(f"/api/decks/{deck_id}")
        self.assertEqual(del_res.status_code, 200)

    def test_03_get_quizzes_and_session_navigation(self) -> None:
        # Lấy danh sách quiz
        res = self.client.get("/api/quizzes")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)

        # Tìm bài quiz có ít nhất 2 câu hỏi để kiểm thử Stack
        multi_q_quizzes = [q for q in data["items"] if len(q.get("questions", [])) >= 2]
        if multi_q_quizzes:
            quiz = multi_q_quizzes[0]
            quiz_id = quiz.get("quiz_id") or int(quiz["id"])

            # Bắt đầu làm bài thi (2-Stack QuizSession)
            start_res = self.client.post(f"/api/quizzes/{quiz_id}/start")
            self.assertEqual(start_res.status_code, 200)
            session = start_res.json()
            attempt_id = session["attempt_id"]
            self.assertFalse(session["can_back"])  # Câu đầu tiên không thể back

            # Chọn đáp án A cho câu hiện tại
            ans_res = self.client.post(
                f"/api/quizzes/session/{attempt_id}/answer",
                json={"selected_answer": "A"},
            )
            self.assertEqual(ans_res.status_code, 200)
            ans_data = ans_res.json()
            self.assertTrue(ans_data["can_back"])  # Đã có câu hỏi trong _back_stack

            # Quay lại câu hỏi trước (Back Stack)
            back_res = self.client.post(f"/api/quizzes/session/{attempt_id}/back")
            self.assertEqual(back_res.status_code, 200)
            back_data = back_res.json()
            self.assertTrue(back_data["can_forward"])  # Đã có câu hỏi trong _forward_stack

            # Nộp bài thi
            submit_res = self.client.post(
                f"/api/quizzes/session/{attempt_id}/submit",
                json={"selected_answers": {}},
            )
            self.assertEqual(submit_res.status_code, 200)
            result = submit_res.json()
            self.assertIn("attempt", result)
            self.assertIn("answers", result)

    def test_04_history_list(self) -> None:
        res = self.client.get("/api/history")
        self.assertEqual(res.status_code, 200)
        self.assertIsInstance(res.json(), list)


if __name__ == "__main__":
    unittest.main()
