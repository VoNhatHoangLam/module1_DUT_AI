"""Kiểm thử tiện ích import_cards_from_csv."""

import tempfile
import unittest
from pathlib import Path

from utils import CsvImporter, import_cards_from_csv


class CsvImporterTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        self.importer = CsvImporter()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_class_instantiation_and_import(self) -> None:
        csv_file = self.temp_path / "cards_class.csv"
        csv_file.write_text(
            "front_text,back_text\nHello,Xin chào\nWorld,Thế giới\n",
            encoding="utf-8",
        )
        cards = self.importer.import_cards(csv_file)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Hello")
        self.assertEqual(cards[0]["back_text"], "Xin chào")

    def test_import_from_csv_standard_headers(self) -> None:
        csv_file = self.temp_path / "cards.csv"
        csv_file.write_text(
            "front_text,back_text\nApple,Quả táo\nBanana,Quả chuối\n",
            encoding="utf-8",
        )
        cards = import_cards_from_csv(csv_file)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Apple")
        self.assertEqual(cards[0]["back_text"], "Quả táo")
        self.assertEqual(cards[0]["position"], 1)
        self.assertEqual(cards[1]["front_text"], "Banana")
        self.assertEqual(cards[1]["back_text"], "Quả chuối")
        self.assertEqual(cards[1]["position"], 2)

    def test_import_from_csv_term_definition_headers(self) -> None:
        csv_content = "term,definition\nAlgorithm,Thuật toán\nData Structure,Cấu trúc dữ liệu\n"
        cards = import_cards_from_csv(csv_content)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Algorithm")
        self.assertEqual(cards[0]["back_text"], "Thuật toán")

    def test_import_from_tsv_and_semicolon(self) -> None:
        tsv_content = "front\tback\nHello\tXin chào\nWorld\tThế giới\n"
        cards = import_cards_from_csv(tsv_content)
        self.assertEqual(len(cards), 2)
        self.assertEqual(cards[0]["front_text"], "Hello")
        self.assertEqual(cards[0]["back_text"], "Xin chào")

        semi_content = "front_text;back_text\nOne;Một\nTwo;Hai\n"
        cards_semi = import_cards_from_csv(semi_content)
        self.assertEqual(len(cards_semi), 2)
        self.assertEqual(cards_semi[0]["front_text"], "One")

    def test_import_empty_file_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            self.importer.import_cards("")

    def test_import_nonexistent_file_raises_file_not_found(self) -> None:
        with self.assertRaises(FileNotFoundError):
            self.importer.import_cards(self.temp_path / "does_not_exist.csv")


if __name__ == "__main__":
    unittest.main()
