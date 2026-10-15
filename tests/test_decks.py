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


if __name__ == "__main__":
    unittest.main()
