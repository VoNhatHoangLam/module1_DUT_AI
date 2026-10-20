"""Kiểm thử tích hợp cho 3 chức năng Backend:
1. POST /api/decks/import (Phân tích CSV flashcard qua CsvImporter)
2. POST /api/quizzes/import (Phân tích CSV câu hỏi quiz qua QuizService)
3. GET /api/quizzes?keyword=... (Tìm kiếm danh sách Quiz)
"""

import unittest
from fastapi.testclient import TestClient

from main import app


class BackendImportAndQuizSearchTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    # -------------------------------------------------------------------------
    # 1. Tests for POST /api/decks/import
    # -------------------------------------------------------------------------

    def test_import_cards_valid_comma_csv(self) -> None:
        csv_data = (
            "front_text,back_text\n"
            "Hello,Xin chao\n"
            "Goodbye,Tam biet\n"
        )
        response = self.client.post("/api/decks/import", json={"csv_content": csv_data})
        self.assertEqual(response.status_code, 200)
        cards = response.json()
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Hello")
        self.assertEqual(cards[0]["back_text"], "Xin chao")
        self.assertEqual(cards[0]["position"], 1)
        self.assertEqual(cards[1]["front_text"], "Goodbye")
        self.assertEqual(cards[1]["back_text"], "Tam biet")
        self.assertEqual(cards[1]["position"], 2)

    def test_import_cards_valid_term_definition_headers(self) -> None:
        csv_data = (
            "term,definition\n"
            "CPU,Bo vi xu ly trung tam\n"
            "RAM,Bo nho truy xuat ngau nhien\n"
        )
        response = self.client.post("/api/decks/import", json={"csv_content": csv_data})
        self.assertEqual(response.status_code, 200)
        cards = response.json()
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "CPU")
        self.assertEqual(cards[0]["back_text"], "Bo vi xu ly trung tam")

    def test_import_cards_valid_semicolon_delimited(self) -> None:
        csv_data = "front_text;back_text\nPython;Ngon ngu lap trinh\nJava;Ngon ngu huong doi tuong"
        response = self.client.post("/api/decks/import", json={"csv_content": csv_data})
        self.assertEqual(response.status_code, 200)
        cards = response.json()
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Python")

    def test_import_cards_invalid_empty_content(self) -> None:
        response = self.client.post("/api/decks/import", json={"csv_content": "   \n\n  "})
        self.assertEqual(response.status_code, 400)

    def test_import_cards_invalid_missing_columns(self) -> None:
        csv_data = "single_column\nrow1\nrow2\n"
        response = self.client.post("/api/decks/import", json={"csv_content": csv_data})
        self.assertEqual(response.status_code, 400)

    # -------------------------------------------------------------------------
    # 2. Tests for POST /api/quizzes/import
    # -------------------------------------------------------------------------

    def test_import_quiz_questions_valid(self) -> None:
        csv_data = (
            "question_text,option_a,option_b,option_c,option_d,correct_answer,points\n"
            "Do phuc tap cua QuickSort trung binh la?,O(n),O(n log n),O(n^2),O(1),B,1.0\n"
            "Stack hoat dong theo nguyen tac gi?,FIFO,LIFO,Priority,Random,B,1.5\n"
        )
        response = self.client.post("/api/quizzes/import", json={"csv_content": csv_data})
        self.assertEqual(response.status_code, 200)
        questions = response.json()
        self.assertEqual(len(questions), 2)
        self.assertEqual(questions[0]["question"], "Do phuc tap cua QuickSort trung binh la?")
        self.assertEqual(questions[0]["optionA"], "O(n)")
        self.assertEqual(questions[0]["optionB"], "O(n log n)")
        self.assertEqual(questions[0]["correctAnswer"], "B")
        self.assertEqual(questions[0]["points"], 1.0)
        self.assertEqual(questions[1]["question"], "Stack hoat dong theo nguyen tac gi?")
        self.assertEqual(questions[1]["correctAnswer"], "B")
        self.assertEqual(questions[1]["points"], 1.5)

    def test_import_quiz_questions_invalid_empty(self) -> None:
        response = self.client.post("/api/quizzes/import", json={"csv_content": ""})
        self.assertEqual(response.status_code, 400)

    def test_import_quiz_questions_invalid_format(self) -> None:
        response = self.client.post("/api/quizzes/import", json={"csv_content": "invalid_header_only\n123\n"})
        self.assertEqual(response.status_code, 400)

    # -------------------------------------------------------------------------
    # 3. Tests for GET /api/quizzes (Search & Pagination)
    # -------------------------------------------------------------------------

    def test_get_quizzes_without_keyword(self) -> None:
        response = self.client.get("/api/quizzes")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("items", data)
        self.assertIn("total_pages", data)
        self.assertIn("page", data)
        self.assertIn("page_size", data)
        self.assertIsInstance(data["items"], list)

    def test_get_quizzes_with_matching_keyword(self) -> None:
        # First retrieve all quizzes to find a sample title
        all_res = self.client.get("/api/quizzes")
        self.assertEqual(all_res.status_code, 200)
        all_data = all_res.json()
        if len(all_data["items"]) > 0:
            sample_title = all_data["items"][0]["title"]
            keyword = sample_title[:4].strip()
            if keyword:
                search_res = self.client.get(f"/api/quizzes?keyword={keyword}")
                self.assertEqual(search_res.status_code, 200)
                search_data = search_res.json()
                self.assertGreater(len(search_data["items"]), 0)
                # Verify that each returned item matches keyword in title or description
                for item in search_data["items"]:
                    matches = (
                        keyword.lower() in item["title"].lower()
                        or keyword.lower() in (item["description"] or "").lower()
                    )
                    self.assertTrue(matches)

    def test_get_quizzes_with_non_matching_keyword(self) -> None:
        search_res = self.client.get("/api/quizzes?keyword=NonExistentKeywordXYZ99999")
        self.assertEqual(search_res.status_code, 200)
        data = search_res.json()
        self.assertEqual(len(data["items"]), 0)
        self.assertEqual(data["total_pages"], 0)


if __name__ == "__main__":
    unittest.main()
