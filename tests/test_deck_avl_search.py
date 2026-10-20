"""Kiểm thử chuyên biệt cho chức năng tìm kiếm Bộ Thẻ bằng Cây AVL (Module 1 - DSA)."""

import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from main import app
from models import Card, Deck
from repositories import CsvRepository
from services import DeckService
from utils import MultiAVLTree


class MultiAVLTreePrefixTestCase(unittest.TestCase):
    def test_multi_avl_tree_prefix_search_and_ordering(self) -> None:
        tree: MultiAVLTree[str, str] = MultiAVLTree()
        # Chèn các khóa đã được chuẩn hóa chữ thường
        tree.insert("từ vựng tiếng anh", "Deck1")
        tree.insert("từ vựng tiếng nhật", "Deck2")
        tree.insert("toán rời rạc", "Deck3")
        tree.insert("english vocabulary", "Deck4")

        # Tìm kiếm tiền tố "từ"
        results_tu = tree.prefix_search("từ")
        self.assertEqual(results_tu, ["Deck1", "Deck2"])

        # Tìm kiếm tiền tố "toán"
        results_toan = tree.prefix_search("toán")
        self.assertEqual(results_toan, ["Deck3"])

        # Tìm kiếm tiền tố "eng"
        results_eng = tree.prefix_search("eng")
        self.assertEqual(results_eng, ["Deck4"])

        # Tiền tố không tồn tại
        results_none = tree.prefix_search("xyz")
        self.assertEqual(results_none, [])


class CsvRepositoryPrefixSearchTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.path = Path(self.temporary_directory.name)
        deck_csv = self.path / "decks.csv"
        deck_csv.write_text(
            "deck_id,title,description,total_cards,is_studied,is_deleted,created_at,updated_at\n",
            encoding="utf-8",
        )
        self.deck_repo = CsvRepository(
            deck_csv,
            Deck,
            "deck_id",
            indexed_fields=("title",),
        )

        # Thêm các bộ thẻ thử nghiệm với chữ hoa/thường đa dạng
        self.deck_repo.add(Deck(deck_id=1, title="Từ vựng IELTS Band 7.0", description="Mô tả 1", is_deleted=False))
        self.deck_repo.add(Deck(deck_id=2, title="Từ vựng Tiếng Nhật N3", description="Mô tả 2", is_deleted=False))
        self.deck_repo.add(Deck(deck_id=3, title="Toán Rời Rạc 1", description="Mô tả 3", is_deleted=False))
        self.deck_repo.add(Deck(deck_id=4, title="English Communication", description="Mô tả 4", is_deleted=False))
        self.deck_repo.add(Deck(deck_id=5, title="Từ vựng Đã Bị Xóa", description="Đã xóa", is_deleted=True))

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_case_insensitive_prefix_search_with_criteria(self) -> None:
        # 1. Tìm bằng chữ thường "từ" -> Khớp cả "Từ vựng IELTS..." và "Từ vựng Tiếng Nhật...", loại trừ deck bị xóa
        results = self.deck_repo.find_by_prefix("title", "từ", is_deleted=False)
        matched_ids = [d.deck_id for d in results]
        self.assertEqual(matched_ids, [1, 2])

        # 2. Tìm bằng chữ HOA "TỪ" -> Vẫn khớp chính xác (không phân biệt hoa thường)
        results_upper = self.deck_repo.find_by_prefix("title", "TỪ", is_deleted=False)
        self.assertEqual([d.deck_id for d in results_upper], [1, 2])

        # 3. Tìm bằng "eng" chữ thường -> Khớp "English Communication"
        results_eng = self.deck_repo.find_by_prefix("title", "eng", is_deleted=False)
        self.assertEqual(len(results_eng), 1)
        self.assertEqual(results_eng[0].title, "English Communication")

        # 4. Tìm bằng "ENGLISH" chữ HOA
        results_eng_upper = self.deck_repo.find_by_prefix("title", "ENGLISH", is_deleted=False)
        self.assertEqual(len(results_eng_upper), 1)
        self.assertEqual(results_eng_upper[0].deck_id, 4)

        # 5. Tiền tố không khớp
        results_empty = self.deck_repo.find_by_prefix("title", "không_tồn_tại", is_deleted=False)
        self.assertEqual(results_empty, [])

    def test_update_maintains_secondary_index(self) -> None:
        # Cập nhật tiêu đề của deck 4 từ "English Communication" sang "Advanced English"
        deck = self.deck_repo.get_by_id(4)
        self.assertIsNotNone(deck)
        deck.title = "Advanced English"
        self.deck_repo.update(deck)

        # Tìm lại bằng "eng" -> không còn khớp deck 4
        res_old = self.deck_repo.find_by_prefix("title", "eng", is_deleted=False)
        self.assertEqual(res_old, [])

        # Tìm bằng "adv" -> khớp deck 4
        res_new = self.deck_repo.find_by_prefix("title", "adv", is_deleted=False)
        self.assertEqual(len(res_new), 1)
        self.assertEqual(res_new[0].deck_id, 4)


class DeckServicePrefixSearchTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        path = Path(self.temporary_directory.name)

        deck_csv = path / "decks.csv"
        deck_csv.write_text(
            "deck_id,title,description,total_cards,is_studied,is_deleted,created_at,updated_at\n",
            encoding="utf-8",
        )
        card_csv = path / "cards.csv"
        card_csv.write_text(
            "card_id,deck_id,front_text,back_text,position\n",
            encoding="utf-8",
        )

        self.deck_repo = CsvRepository(deck_csv, Deck, "deck_id", indexed_fields=("title",))
        self.card_repo = CsvRepository(card_csv, Card, "card_id", indexed_fields=("deck_id",))
        self.service = DeckService(self.deck_repo, self.card_repo)

        # Thêm dữ liệu mẫu
        self.deck_repo.add(Deck(deck_id=1, title="Từ vựng Chuyên ngành CNTT", description="Bộ thẻ IT", is_deleted=False))
        self.deck_repo.add(Deck(deck_id=2, title="Từ vựng Tiếng Pháp cơ bản", description="Bộ thẻ Pháp", is_deleted=False))
        self.deck_repo.add(Deck(deck_id=3, title="Lập trình Python", description="Chứa từ vựng trong mô tả", is_deleted=False))

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_search_decks_by_title_prefix_only(self) -> None:
        # Tìm tiền tố "từ" -> Khớp deck 1 và 2
        matched = self.service.search_decks_by_title_prefix("từ")
        self.assertEqual([d.deck_id for d in matched], [1, 2])

        # Đảm bảo CHỈ tìm kiếm theo title, không tìm theo description:
        # Deck 3 có "từ vựng" trong description nhưng title là "Lập trình Python", không được khớp
        for d in matched:
            self.assertNotEqual(d.deck_id, 3)

    def test_get_decks_pagination_with_keyword(self) -> None:
        res = self.service.get_decks(keyword="từ", page=1, page_size=1)
        self.assertEqual(res["total_pages"], 2)
        self.assertEqual(res["page"], 1)
        self.assertEqual(len(res["items"]), 1)
        self.assertEqual(res["items"][0].deck_id, 1)

        res_p2 = self.service.get_decks(keyword="từ", page=2, page_size=1)
        self.assertEqual(len(res_p2["items"]), 1)
        self.assertEqual(res_p2["items"][0].deck_id, 2)


class ApiDeckSearchIntegrationTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_api_get_decks_prefix_search_by_title(self) -> None:
        # Gọi endpoint /api/decks kèm keyword
        res = self.client.get("/api/decks?keyword=t")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("items", data)
        self.assertIn("total_pages", data)
        for item in data["items"]:
            # Mọi item trả về phải có title bắt đầu bằng "t" (case-insensitive)
            title = item.get("title") or item.get("name") or ""
            self.assertTrue(title.lower().startswith("t"), f"Item {title} không bắt đầu bằng 't'")


if __name__ == "__main__":
    unittest.main()
