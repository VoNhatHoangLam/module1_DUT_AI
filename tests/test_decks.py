"""Kiểm thử chức năng bộ thẻ (decks)."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from models import Card, Deck
from repositories import CsvRepository
from services import DeckService


class DeckServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temporary_directory.name)

        self.decks_file = self.temp_path / "decks.csv"
        self.decks_file.write_text(
            "deck_id,title,description,total_cards,is_studied,is_deleted,created_at,updated_at\n",
            encoding="utf-8",
        )
        self.deck_repo = CsvRepository(self.decks_file, Deck, "deck_id")

        self.cards_file = self.temp_path / "cards.csv"
        self.cards_file.write_text(
            "card_id,deck_id,front_text,back_text,position\n",
            encoding="utf-8",
        )
        self.card_repo = CsvRepository(self.cards_file, Card, "card_id")
        self.service = DeckService(
            deck_repository=self.deck_repo,
            card_repository=self.card_repo,
        )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_create_deck_with_cards(self) -> None:
        card_list = [
            {"front_text": "Apple", "back_text": "Quả táo", "position": 1}
        ]
        deck_id, title, description, updated_at, card_count, cards = (
            self.service.create_deck(
                title="Từ vựng tiếng Anh cơ bản",
                description="Bộ từ vựng demo bài test",
                cards=card_list,
            )
        )

        self.assertEqual(deck_id, 1)
        self.assertEqual(title, "Từ vựng tiếng Anh cơ bản")
        self.assertEqual(description, "Bộ từ vựng demo bài test")
        self.assertIsInstance(updated_at, datetime)
        self.assertEqual(card_count, 1)
        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].front_text, "Apple")
        self.assertEqual(cards[0].back_text, "Quả táo")

    def test_create_deck_without_cards(self) -> None:
        deck_id, title, description, updated_at, card_count, cards = (
            self.service.create_deck(
                title="Bộ thẻ trống",
            )
        )

        self.assertEqual(deck_id, 1)
        self.assertEqual(title, "Bộ thẻ trống")
        self.assertIsNone(description)
        self.assertIsInstance(updated_at, datetime)
        self.assertEqual(card_count, 0)
        self.assertEqual(cards, [])

    def test_create_deck_empty_title_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_deck(title="   ")

    def test_get_deck_by_id(self) -> None:
        self.service.create_deck(title="Bộ 1", description="Mô tả 1")
        deck = self.service.get_deck_by_id(1)
        self.assertIsNotNone(deck)
        self.assertEqual(deck.title, "Bộ 1")

        non_existent = self.service.get_deck_by_id(999)
        self.assertIsNone(non_existent)

    def test_delete_deck_soft_delete(self) -> None:
        self.service.create_deck(title="Bộ cần xóa")
        self.assertTrue(self.service.delete_deck(1))

        # get_deck_by_id không trả về deck đã xóa
        self.assertIsNone(self.service.get_deck_by_id(1))
        # Bản ghi trong repository được đánh dấu is_deleted=True (Soft delete)
        repo_deck = self.deck_repo.get_by_id(1)
        self.assertIsNotNone(repo_deck)
        self.assertTrue(repo_deck.is_deleted)

        # Xóa lại lần nữa phải ném RecordNotFoundError
        from repositories import RecordNotFoundError
        with self.assertRaises(RecordNotFoundError):
            self.service.delete_deck(1)

    def test_get_all_decks(self) -> None:
        self.service.create_deck(title="Deck A")
        self.service.create_deck(title="Deck B")
        self.service.create_deck(title="Deck C")

        all_active = self.service.get_all_decks()
        self.assertEqual(len(all_active), 3)

        self.service.delete_deck(2)
        remaining = self.service.get_all_decks()
        self.assertEqual(len(remaining), 2)
        titles = [d.title for d in remaining]
        self.assertIn("Deck A", titles)
        self.assertIn("Deck C", titles)
        self.assertNotIn("Deck B", titles)

    def test_search_deck_by_title_and_prefix(self) -> None:
        self.service.create_deck(title="Tiếng Anh Giao Tiếp")
        self.service.create_deck(title="Tiếng Anh Chuyên Ngành")
        self.service.create_deck(title="Toán Rời Rạc")

        # Tìm kiếm chính xác O(log N)
        exact = self.service.search_deck_by_title("Toán Rời Rạc")
        self.assertEqual(len(exact), 1)
        self.assertEqual(exact[0].title, "Toán Rời Rạc")

        # Tìm kiếm theo tiền tố O(log N + K)
        prefix_matches = self.service.search_decks_by_title_prefix("Tiếng Anh")
        self.assertEqual(len(prefix_matches), 2)

        # Tìm kiếm đa năng bằng search_decks
        by_id = self.service.search_decks("1")
        self.assertEqual(len(by_id), 1)
        self.assertEqual(by_id[0].title, "Tiếng Anh Giao Tiếp")

    def test_get_cards_by_deck_id(self) -> None:
        cards_input = [
            {"front_text": "Front 1", "back_text": "Back 1", "position": 2},
            {"front_text": "Front 2", "back_text": "Back 2", "position": 1},
        ]
        self.service.create_deck(title="Deck có thẻ", cards=cards_input)
        cards = self.service.get_cards_by_deck_id(1)
        self.assertEqual(len(cards), 2)
        # Kiểm tra được sắp xếp theo position tăng dần
        self.assertEqual(cards[0].position, 1)
        self.assertEqual(cards[1].position, 2)

    def test_deck_service_import_cards_from_csv_does_not_create_deck(self) -> None:
        csv_content = "front_text,back_text\nHello,Xin chào\nWorld,Thế giới\n"
        cards = self.service.import_cards_from_csv(csv_content)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Hello")

        # Đảm bảo KHÔNG tự động lưu vào database decks.csv khi chỉ mới import
        all_decks = self.service.get_all_decks()
        self.assertEqual(len(all_decks), 0)


if __name__ == "__main__":
    unittest.main()
