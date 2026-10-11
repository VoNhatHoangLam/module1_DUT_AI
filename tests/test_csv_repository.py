"""Kiểm thử tầng lưu trữ CSV."""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from models import Card
from repositories import (
    CsvRepository,
    CsvSchemaError,
    RecordNotFoundError,
    create_repositories,
)


class CsvRepositoryTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temporary_directory.name) / "cards.csv"
        self.file_path.write_text(
            "card_id,deck_id,front_text,back_text,position,is_deleted,created_at,updated_at\n"
            "100,10,Apple,Quả táo,1,0,2026-10-10 10:05:00,2026-10-10 10:05:00\n",
            encoding="utf-8",
        )
        self.repository = CsvRepository(self.file_path, Card, "card_id")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_get_all_converts_csv_values_to_model_types(self) -> None:
        cards = self.repository.get_all()

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0].card_id, 100)
        self.assertEqual(cards[0].back_text, "Quả táo")
        self.assertFalse(cards[0].is_deleted)
        self.assertEqual(cards[0].created_at, datetime(2026, 10, 10, 10, 5))

    def test_add_generates_next_id_and_persists_record(self) -> None:
        card = Card(
            deck_id=10,
            front_text="Banana",
            back_text="Quả chuối",
            position=2,
        )

        saved_card = self.repository.add(card)
        reloaded_card = self.repository.get_by_id(101)

        self.assertEqual(saved_card.card_id, 101)
        self.assertEqual(reloaded_card, saved_card)

    def test_update_replaces_existing_record(self) -> None:
        card = self.repository.get_by_id(100)
        self.assertIsNotNone(card)
        card.back_text = "Trái táo"

        self.repository.update(card)

        self.assertEqual(self.repository.get_by_id(100).back_text, "Trái táo")

    def test_update_raises_when_record_does_not_exist(self) -> None:
        card = Card(
            card_id=999,
            deck_id=10,
            front_text="Missing",
            back_text="Không tồn tại",
            position=2,
        )

        with self.assertRaises(RecordNotFoundError):
            self.repository.update(card)

    def test_rejects_header_that_does_not_match_model(self) -> None:
        self.file_path.write_text("card_id,deck_id\n1,10\n", encoding="utf-8")

        with self.assertRaises(CsvSchemaError):
            self.repository.get_all()


class RealDataSmokeTestCase(unittest.TestCase):
    def test_all_project_csv_files_match_their_models(self) -> None:
        repositories = create_repositories()

        self.assertEqual(len(repositories), 10)
        for repository in repositories.values():
            repository.get_all()


if __name__ == "__main__":
    unittest.main()
