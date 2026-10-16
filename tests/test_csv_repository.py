"""Kiểm thử toàn diện tầng lưu trữ CSV kết hợp Chỉ mục Cây AVL.

Bao phủ 100% các hàm, phương thức (public & private/helper), ngoại lệ,
cơ chế chuyển đổi kiểu (serialization/deserialization) và đồng bộ cache.
"""

from __future__ import annotations

import tempfile
import time
import unittest
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Optional, Union

from models import Card
from repositories import (
    CsvDataError,
    CsvRepository,
    CsvRepositoryError,
    CsvSchemaError,
    DuplicateKeyError,
    RecordNotFoundError,
    create_repositories,
)


@dataclass(kw_only=True, slots=True)
class DummyItem:
    """Model phụ trợ dùng cho việc kiểm thử chuyển đổi đa kiểu dữ liệu."""

    item_id: Optional[int] = None
    name: str
    is_active: bool = True
    price: Decimal = Decimal("0.0")
    created_at: Optional[datetime] = None


class CsvRepositoryInitTestCase(unittest.TestCase):
    """Kiểm thử hàm __init__ và xác thực tham số đầu vào."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "items.csv"
        self.file_path.write_text(
            "item_id,name,is_active,price,created_at\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_init_success_with_valid_parameters(self) -> None:
        repo = CsvRepository(
            self.file_path,
            DummyItem,
            "item_id",
            indexed_fields=("name",),
        )
        self.assertEqual(repo.file_path, self.file_path)
        self.assertEqual(repo.model_class, DummyItem)
        self.assertEqual(repo.id_field, "item_id")
        self.assertEqual(repo._indexed_fields, ("name",))
        self.assertIn("name", repo._secondary_indices)

    def test_init_raises_when_model_is_not_dataclass(self) -> None:
        class NotADataclass:
            pass

        with self.assertRaises(TypeError) as ctx:
            CsvRepository(self.file_path, NotADataclass, "item_id")
        self.assertIn("phải là một dataclass", str(ctx.exception))

    def test_init_raises_when_id_field_not_in_model(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            CsvRepository(self.file_path, DummyItem, "invalid_id_field")
        self.assertIn("không có trường khóa chính", str(ctx.exception))

    def test_init_raises_when_indexed_field_not_in_model(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            CsvRepository(
                self.file_path,
                DummyItem,
                "item_id",
                indexed_fields=("non_existent_column",),
            )
        self.assertIn("không có trường chỉ mục phụ", str(ctx.exception))


class CsvRepositoryCrudTestCase(unittest.TestCase):
    """Kiểm thử các thao tác CRUD: get_all, get_by_id, exists, find_by, add, update, _next_id."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "cards.csv"
        self.file_path.write_text(
            "card_id,deck_id,front_text,back_text,position\n"
            "100,10,Apple,Quả táo,1\n"
            "101,10,Banana,Quả chuối,2\n"
            "\n"  # Dòng trống để kiểm tra bỏ qua dòng rỗng
            "102,20,Cat,Con mèo,1\n",
            encoding="utf-8",
        )
        self.repo = CsvRepository(
            self.file_path,
            Card,
            "card_id",
            indexed_fields=("deck_id",),
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_get_all_reads_all_valid_records_ignoring_blank_lines(self) -> None:
        cards = self.repo.get_all()
        self.assertEqual(len(cards), 3)
        self.assertEqual([c.card_id for c in cards], [100, 101, 102])

    def test_get_by_id_and_exists(self) -> None:
        self.assertTrue(self.repo.exists(100))
        self.assertTrue(self.repo.exists(101))
        self.assertFalse(self.repo.exists(999))

        card = self.repo.get_by_id(100)
        self.assertIsNotNone(card)
        self.assertEqual(card.front_text, "Apple")

        missing = self.repo.get_by_id(999)
        self.assertIsNone(missing)

    def test_find_by_with_indexed_field(self) -> None:
        deck_10_cards = self.repo.find_by(deck_id=10)
        self.assertEqual(len(deck_10_cards), 2)
        self.assertEqual([c.card_id for c in deck_10_cards], [100, 101])

        deck_20_cards = self.repo.find_by(deck_id=20)
        self.assertEqual(len(deck_20_cards), 1)
        self.assertEqual(deck_20_cards[0].front_text, "Cat")

        deck_empty = self.repo.find_by(deck_id=999)
        self.assertEqual(deck_empty, [])

    def test_find_by_with_multiple_criteria(self) -> None:
        # 1 trường có chỉ mục phụ + 1 trường không có chỉ mục phụ
        res = self.repo.find_by(deck_id=10, position=2)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].front_text, "Banana")

        # Điều kiện không thỏa mãn
        res_none = self.repo.find_by(deck_id=10, position=99)
        self.assertEqual(res_none, [])

    def test_find_by_without_indexed_field(self) -> None:
        # Tìm theo front_text (chưa được đánh chỉ mục)
        res = self.repo.find_by(front_text="Apple")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].card_id, 100)

        missing = self.repo.find_by(front_text="NonExistent")
        self.assertEqual(missing, [])

    def test_find_by_raises_when_criteria_has_unknown_field(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            self.repo.find_by(unknown_column="abc")
        self.assertIn("Model không có trường: unknown_column", str(ctx.exception))

    def test_add_with_auto_generated_id(self) -> None:
        new_card = Card(
            deck_id=10,
            front_text="Dog",
            back_text="Con chó",
            position=3,
        )
        saved = self.repo.add(new_card)

        # ID lớn nhất hiện tại là 102, nên tự sinh là 103
        self.assertEqual(saved.card_id, 103)
        self.assertTrue(self.repo.exists(103))
        self.assertEqual(len(self.repo.get_all()), 4)

        # Kiểm tra chỉ mục phụ được cập nhật
        deck_10_cards = self.repo.find_by(deck_id=10)
        self.assertEqual(len(deck_10_cards), 3)

    def test_add_with_preset_id(self) -> None:
        new_card = Card(
            card_id=200,
            deck_id=30,
            front_text="Elephant",
            back_text="Con voi",
            position=1,
        )
        saved = self.repo.add(new_card)
        self.assertEqual(saved.card_id, 200)
        self.assertEqual(self.repo.get_by_id(200).front_text, "Elephant")

    def test_add_duplicate_key_raises_duplicate_key_error(self) -> None:
        duplicate = Card(
            card_id=100,
            deck_id=10,
            front_text="Duplicate",
            back_text="Trùng",
            position=1,
        )
        with self.assertRaises(DuplicateKeyError):
            self.repo.add(duplicate)

    def test_add_wrong_record_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.repo.add("not a card object")  # type: ignore

    def test_update_success(self) -> None:
        card = self.repo.get_by_id(100)
        self.assertIsNotNone(card)
        card.front_text = "Apple Red"
        card.back_text = "Quả táo đỏ"

        updated = self.repo.update(card)
        self.assertEqual(updated.front_text, "Apple Red")

        reloaded = self.repo.get_by_id(100)
        self.assertEqual(reloaded.front_text, "Apple Red")
        self.assertEqual(reloaded.back_text, "Quả táo đỏ")

    def test_update_modifies_secondary_index_bucket(self) -> None:
        # Chuyển thẻ 100 từ deck_id=10 sang deck_id=50
        card = self.repo.get_by_id(100)
        card.deck_id = 50
        self.repo.update(card)

        # Cũ: deck_id=10 chỉ còn thẻ 101
        deck_10_cards = self.repo.find_by(deck_id=10)
        self.assertEqual(len(deck_10_cards), 1)
        self.assertEqual(deck_10_cards[0].card_id, 101)

        # Mới: deck_id=50 có thẻ 100
        deck_50_cards = self.repo.find_by(deck_id=50)
        self.assertEqual(len(deck_50_cards), 1)
        self.assertEqual(deck_50_cards[0].card_id, 100)

    def test_update_raises_when_id_is_none(self) -> None:
        card = Card(
            card_id=None,
            deck_id=10,
            front_text="No ID",
            back_text="Không ID",
            position=1,
        )
        with self.assertRaises(ValueError) as ctx:
            self.repo.update(card)
        self.assertIn("chưa có khóa chính", str(ctx.exception))

    def test_update_raises_when_record_not_found(self) -> None:
        card = Card(
            card_id=999,
            deck_id=10,
            front_text="Missing",
            back_text="Không tìm thấy",
            position=1,
        )
        with self.assertRaises(RecordNotFoundError):
            self.repo.update(card)

    def test_update_wrong_record_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            self.repo.update({"card_id": 100})  # type: ignore

    def test_next_id_starts_at_one_for_empty_dataset(self) -> None:
        empty_file = Path(self.temp_dir.name) / "empty_cards.csv"
        empty_file.write_text(
            "card_id,deck_id,front_text,back_text,position\n",
            encoding="utf-8",
        )
        empty_repo = CsvRepository(empty_file, Card, "card_id")
        self.assertEqual(empty_repo._next_id(), 1)


class CsvRepositorySerializationTestCase(unittest.TestCase):
    """Kiểm thử các hàm _deserialize, _serialize, _unwrap_optional với mọi kiểu dữ liệu."""

    def test_deserialize_string(self) -> None:
        self.assertEqual(CsvRepository._deserialize("hello", str), "hello")
        self.assertEqual(CsvRepository._deserialize("", str), "")

    def test_deserialize_int(self) -> None:
        self.assertEqual(CsvRepository._deserialize("123", int), 123)
        self.assertEqual(CsvRepository._deserialize("-45", int), -45)
        with self.assertRaises(ValueError):
            CsvRepository._deserialize("not_an_int", int)

    def test_deserialize_bool(self) -> None:
        self.assertTrue(CsvRepository._deserialize("1", bool))
        self.assertTrue(CsvRepository._deserialize("true", bool))
        self.assertTrue(CsvRepository._deserialize("TRUE", bool))
        self.assertFalse(CsvRepository._deserialize("0", bool))
        self.assertFalse(CsvRepository._deserialize("false", bool))
        self.assertFalse(CsvRepository._deserialize("False", bool))

        with self.assertRaises(ValueError):
            CsvRepository._deserialize("yes", bool)
        with self.assertRaises(ValueError):
            CsvRepository._deserialize("2", bool)

    def test_deserialize_datetime(self) -> None:
        dt = CsvRepository._deserialize("2026-10-15 12:30:45", datetime)
        self.assertEqual(dt, datetime(2026, 10, 15, 12, 30, 45))

        with self.assertRaises(ValueError):
            CsvRepository._deserialize("invalid-date-format", datetime)

    def test_deserialize_decimal(self) -> None:
        d = CsvRepository._deserialize("99.95", Decimal)
        self.assertEqual(d, Decimal("99.95"))

        with self.assertRaises(Exception):
            CsvRepository._deserialize("not-a-decimal", Decimal)

    def test_deserialize_optional(self) -> None:
        # Khi chuỗi rỗng -> trả về None
        self.assertIsNone(CsvRepository._deserialize("", Optional[int]))
        self.assertIsNone(CsvRepository._deserialize(None, Optional[datetime]))

        # Khi có chuỗi -> parse sang kiểu con
        self.assertEqual(CsvRepository._deserialize("42", Optional[int]), 42)
        self.assertEqual(CsvRepository._deserialize("true", Optional[bool]), True)

    def test_deserialize_unsupported_type_raises_type_error(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            CsvRepository._deserialize("abc", list[int])
        self.assertIn("chưa được hỗ trợ", str(ctx.exception))

    def test_unwrap_optional(self) -> None:
        is_opt, inner = CsvRepository._unwrap_optional(Optional[int])
        self.assertTrue(is_opt)
        self.assertEqual(inner, int)

        is_opt, inner = CsvRepository._unwrap_optional(Union[str, None])
        self.assertTrue(is_opt)
        self.assertEqual(inner, str)

        is_opt, inner = CsvRepository._unwrap_optional(int | None)
        self.assertTrue(is_opt)
        self.assertEqual(inner, int)

        is_opt, inner = CsvRepository._unwrap_optional(str)
        self.assertFalse(is_opt)
        self.assertEqual(inner, str)

    def test_serialize(self) -> None:
        self.assertEqual(CsvRepository._serialize(None), "")
        self.assertEqual(CsvRepository._serialize(True), "1")
        self.assertEqual(CsvRepository._serialize(False), "0")
        self.assertEqual(
            CsvRepository._serialize(datetime(2026, 10, 15, 12, 0, 0)),
            "2026-10-15 12:00:00",
        )
        self.assertEqual(CsvRepository._serialize(Decimal("10.50")), "10.50")
        self.assertEqual(CsvRepository._serialize(100), "100")
        self.assertEqual(CsvRepository._serialize("hello"), "hello")


class CsvRepositoryErrorHandlingTestCase(unittest.TestCase):
    """Kiểm thử các tình huống ngoại lệ: CsvSchemaError, CsvDataError, FileNotFoundError."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_file_not_found_raises_file_not_found_error(self) -> None:
        non_existent_file = Path(self.temp_dir.name) / "not_found.csv"
        repo = CsvRepository(non_existent_file, Card, "card_id")

        with self.assertRaises(FileNotFoundError):
            repo.get_all()

    def test_validate_header_mismatch_raises_csv_schema_error(self) -> None:
        file_path = Path(self.temp_dir.name) / "bad_header.csv"
        # Thiếu cột position
        file_path.write_text("card_id,deck_id,front_text,back_text\n1,10,A,B\n", encoding="utf-8")
        repo = CsvRepository(file_path, Card, "card_id")

        with self.assertRaises(CsvSchemaError) as ctx:
            repo.get_all()
        self.assertIn("phải là", str(ctx.exception))

    def test_row_with_extra_columns_raises_csv_schema_error(self) -> None:
        file_path = Path(self.temp_dir.name) / "extra_cols.csv"
        # Dòng dữ liệu có 6 giá trị trong khi header chỉ có 5
        file_path.write_text(
            "card_id,deck_id,front_text,back_text,position\n"
            "1,10,A,B,1,extra_value\n",
            encoding="utf-8",
        )
        repo = CsvRepository(file_path, Card, "card_id")

        with self.assertRaises(CsvSchemaError) as ctx:
            repo.get_all()
        self.assertIn("có nhiều cột hơn header", str(ctx.exception))

    def test_corrupted_row_data_raises_csv_data_error(self) -> None:
        file_path = Path(self.temp_dir.name) / "corrupted.csv"
        # card_id không phải số nguyên
        file_path.write_text(
            "card_id,deck_id,front_text,back_text,position\n"
            "not_an_int,10,A,B,1\n",
            encoding="utf-8",
        )
        repo = CsvRepository(file_path, Card, "card_id")

        with self.assertRaises(CsvDataError) as ctx:
            repo.get_all()
        self.assertIn("Dữ liệu không hợp lệ tại dòng 2", str(ctx.exception))


class CsvRepositoryCacheSyncTestCase(unittest.TestCase):
    """Kiểm thử tính năng đồng bộ cache, nhận diện thay đổi file và cô lập đối tượng (immutability)."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "cards.csv"
        self.file_path.write_text(
            "card_id,deck_id,front_text,back_text,position\n"
            "1,10,Apple,Quả táo,1\n",
            encoding="utf-8",
        )
        self.repo = CsvRepository(self.file_path, Card, "card_id", indexed_fields=("deck_id",))

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_object_isolation_prevents_unintended_in_place_mutations(self) -> None:
        # Lấy bản ghi ra và sửa thuộc tính trên biến cục bộ
        card = self.repo.get_by_id(1)
        self.assertIsNotNone(card)
        card.front_text = "Mutated Externally"

        # Bản ghi bên trong repo không bị ảnh hưởng vì get_by_id trả về copy
        clean_card = self.repo.get_by_id(1)
        self.assertEqual(clean_card.front_text, "Apple")

    def test_auto_reload_cache_when_file_modified_externally(self) -> None:
        # Lần 1: có 1 bản ghi
        self.assertEqual(len(self.repo.get_all()), 1)

        # Chờ 1 chút hoặc ghi đè file với dữ liệu mới
        time.sleep(0.01)
        self.file_path.write_text(
            "card_id,deck_id,front_text,back_text,position\n"
            "1,10,Apple,Quả táo,1\n"
            "2,10,Orange,Quả cam,2\n",
            encoding="utf-8",
        )

        # Lần 2: repo tự động phát hiện mtime đổi và nạp lại
        cards = self.repo.get_all()
        self.assertEqual(len(cards), 2)
        self.assertEqual(self.repo.get_by_id(2).front_text, "Orange")
        self.assertEqual(len(self.repo.find_by(deck_id=10)), 2)

    def test_write_through_persistence_matches_csv_file_on_disk(self) -> None:
        self.repo.add(Card(card_id=2, deck_id=10, front_text="Pear", back_text="Quả lê", position=2))

        # Đọc trực tiếp nội dung file CSV từ đĩa
        disk_content = self.file_path.read_text(encoding="utf-8")
        self.assertIn("1,10,Apple,Quả táo,1", disk_content)
        self.assertIn("2,10,Pear,Quả lê,2", disk_content)


class CsvRepositoryIntegrationTestCase(unittest.TestCase):
    """Kiểm thử hàm factory create_repositories, dữ liệu thực tế và hiệu năng benchmark."""

    def test_create_repositories_returns_six_configured_repositories(self) -> None:
        repos = create_repositories()

        self.assertEqual(len(repos), 6)
        expected_keys = {
            "decks",
            "cards",
            "quizzes",
            "questions",
            "quiz_attempts",
            "quiz_answers",
        }
        self.assertEqual(set(repos.keys()), expected_keys)

        # Kiểm tra cấu hình chỉ mục phụ của từng repo
        self.assertEqual(repos["cards"]._indexed_fields, ("deck_id",))
        self.assertEqual(repos["questions"]._indexed_fields, ("quiz_id",))
        self.assertEqual(repos["quiz_answers"]._indexed_fields, ("attempt_id",))
        self.assertEqual(repos["quizzes"]._indexed_fields, ("source_deck_id",))
        self.assertEqual(repos["quiz_attempts"]._indexed_fields, ("quiz_id",))
        self.assertEqual(repos["decks"]._indexed_fields, ())

    def test_all_project_csv_files_match_their_models(self) -> None:
        repositories = create_repositories()

        for name, repository in repositories.items():
            records = repository.get_all()
            self.assertIsInstance(records, list)
            # Kiểm tra đọc được ít nhất 1 bản ghi mẫu hiện có
            self.assertGreater(len(records), 0, f"Bảng {name} không có dữ liệu mẫu")

    def test_avl_search_benchmark_scale(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        temp_file = Path(temp_dir.name) / "benchmark_cards.csv"
        temp_file.write_text(
            "card_id,deck_id,front_text,back_text,position\n",
            encoding="utf-8",
        )
        repo = CsvRepository(temp_file, Card, "card_id", indexed_fields=("deck_id",))

        # Thêm 500 bản ghi
        for i in range(1, 501):
            repo.add(Card(deck_id=i % 10, front_text=f"Word {i}", back_text=f"Meaning {i}", position=i))

        # Đo thời gian 1,000 lần tìm kiếm get_by_id (O(log N))
        start_time = time.perf_counter()
        for i in range(1, 1001):
            target_id = (i % 500) + 1
            card = repo.get_by_id(target_id)
            self.assertIsNotNone(card)
        duration = time.perf_counter() - start_time

        # 1,000 lần tìm kiếm trên RAM bằng cây AVL hoàn tất dưới 0.1 giây
        self.assertLess(duration, 0.1)
        temp_dir.cleanup()


if __name__ == "__main__":
    unittest.main()
