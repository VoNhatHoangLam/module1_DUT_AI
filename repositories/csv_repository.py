"""Tầng lưu trữ dữ liệu sử dụng các file CSV kết hợp Chỉ mục Cây AVL O(log N)."""

from __future__ import annotations

import copy
import csv
import os
import tempfile
from dataclasses import fields, is_dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from threading import RLock
from types import UnionType
from typing import (
    Any,
    Generic,
    Iterable,
    Optional,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from config import DATA_DIR
from models import (
    Card,
    Deck,
    Question,
    Quiz,
    QuizAnswer,
    QuizAttempt,
)
from utils import AVLTree, MultiAVLTree


T = TypeVar("T")


class CsvRepositoryError(Exception):
    """Lỗi cơ sở của tầng lưu trữ CSV."""


class CsvSchemaError(CsvRepositoryError):
    """Header của file CSV không khớp với model."""


class DuplicateKeyError(CsvRepositoryError):
    """Khóa chính đã tồn tại."""


class RecordNotFoundError(CsvRepositoryError):
    """Không tìm thấy bản ghi cần cập nhật."""


class CsvDataError(CsvRepositoryError):
    """Một giá trị trong CSV không thể chuyển sang kiểu của model."""


class CsvRepository(Generic[T]):
    """Thực hiện các thao tác lưu trữ cho một dataclass và file CSV.

    Sử dụng Cây AVL tự cân bằng (AVLTree) làm chỉ mục chính (Primary Index)
    và MultiAVLTree làm chỉ mục phụ (Secondary Index) để đảm bảo:
    - `get_by_id`: O(log N)
    - `exists`: O(log N)
    - `find_by`: O(log N) cho các trường có chỉ mục phụ
    - `get_all`: Lấy từ bộ nhớ RAM (In-order traversal), loại bỏ I/O đọc đĩa lặp lại.
    - `add` / `update`: O(log N) trong bộ nhớ kèm ghi đồng bộ an toàn (Write-Through).
    """

    def __init__(
        self,
        file_path: str | Path,
        model_class: type[T],
        id_field: str,
        indexed_fields: Optional[Iterable[str]] = None,
    ) -> None:
        if not is_dataclass(model_class):
            raise TypeError("model_class phải là một dataclass")

        self.file_path = Path(file_path)
        self.model_class = model_class
        self.id_field = id_field
        self._field_names = tuple(field.name for field in fields(model_class))
        self._type_hints = get_type_hints(model_class)
        self._lock = RLock()

        if id_field not in self._field_names:
            raise ValueError(f"Model không có trường khóa chính {id_field!r}")

        # Cấu hình các trường chỉ mục phụ
        self._indexed_fields = tuple(indexed_fields or ())
        for field_name in self._indexed_fields:
            if field_name not in self._field_names:
                raise ValueError(f"Model không có trường chỉ mục phụ {field_name!r}")

        # Chỉ mục chính: Cây AVL mapping id -> record (O(log N))
        self._primary_index: AVLTree[int, T] = AVLTree()

        # Các chỉ mục phụ: Cây MultiAVLTree mapping field_value -> list[record] (O(log N))
        self._secondary_indices: dict[str, MultiAVLTree[Any, T]] = {
            name: MultiAVLTree() for name in self._indexed_fields
        }

        # Dấu vết thời gian sửa file trên đĩa để tự động làm mới cache nếu file bị sửa ngoài
        self._last_mtime: Optional[float] = None
        self._is_loaded: bool = False

    def get_all(self) -> list[T]:
        """Đọc toàn bộ bản ghi và chuyển từng dòng thành model.

        Dữ liệu được duyệt từ cây AVL trong bộ nhớ RAM theo thứ tự tăng dần của khóa chính.
        """
        with self._lock:
            self._ensure_cache_loaded()
            return [copy.copy(record) for record in self._primary_index.inorder()]

    def get_by_id(self, record_id: int) -> Optional[T]:
        """Tìm một bản ghi theo khóa chính với độ phức tạp O(log N).

        Trả về None nếu không tồn tại.
        """
        with self._lock:
            self._ensure_cache_loaded()
            record = self._primary_index.search(record_id)
            return copy.copy(record) if record is not None else None

    def find_by(self, **criteria: Any) -> list[T]:
        """Tìm các bản ghi có tất cả trường khớp với điều kiện truyền vào.

        Nếu trong criteria có trường được đánh chỉ mục phụ, tìm kiếm đạt O(log N).
        """
        unknown_fields = set(criteria) - set(self._field_names)
        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Model không có trường: {names}")

        with self._lock:
            self._ensure_cache_loaded()

            # Kiểm tra xem có trường chỉ mục phụ nào trong criteria không
            indexed_match = next(
                (field for field in criteria if field in self._secondary_indices),
                None,
            )

            if indexed_match is not None:
                # Tìm kiếm O(log N) bằng cây MultiAVLTree
                candidates = self._secondary_indices[indexed_match].search(criteria[indexed_match])
                remaining_criteria = {
                    k: v for k, v in criteria.items() if k != indexed_match
                }
                if not remaining_criteria:
                    return [copy.copy(record) for record in candidates]
                return [
                    copy.copy(record)
                    for record in candidates
                    if all(getattr(record, name) == value for name, value in remaining_criteria.items())
                ]

            # Nếu không có chỉ mục phụ, duyệt trên tập in-memory RAM
            return [
                copy.copy(record)
                for record in self._primary_index.inorder()
                if all(getattr(record, name) == value for name, value in criteria.items())
            ]

    def find_by_prefix(self, field: str, prefix: str) -> list[T]:
        """Tìm các bản ghi có giá trị của trường bắt đầu bằng prefix với độ phức tạp O(log N + K).

        Nếu trường có trong chỉ mục phụ MultiAVLTree, tìm kiếm đạt O(log N + K).
        Nếu không có chỉ mục phụ, duyệt qua toàn bộ các bản ghi trong bộ nhớ RAM.
        """
        if field not in self._field_names:
            raise ValueError(f"Model {self.model_class.__name__} không có trường: {field}")

        prefix_str = str(prefix)
        with self._lock:
            self._ensure_cache_loaded()
            if field in self._secondary_indices:
                candidates = self._secondary_indices[field].prefix_search(prefix_str)
                return [copy.copy(record) for record in candidates]

            return [
                copy.copy(record)
                for record in self._primary_index.inorder()
                if str(getattr(record, field, "")).startswith(prefix_str)
            ]

    def exists(self, record_id: int) -> bool:
        """Kiểm tra một khóa chính có tồn tại hay không với độ phức tạp O(log N)."""
        with self._lock:
            self._ensure_cache_loaded()
            return self._primary_index.contains(record_id)

    def add(self, record: T) -> T:
        """Thêm bản ghi, tự cấp khóa chính nếu model chưa có ID.

        Cập nhật vào Cây AVL với O(log N) và ghi đồng bộ an toàn xuống file CSV.
        """
        self._validate_record_type(record)
        with self._lock:
            self._ensure_cache_loaded()
            current_id = getattr(record, self.id_field)

            if current_id is None:
                current_id = self._next_id()
                setattr(record, self.id_field, current_id)
            elif self._primary_index.contains(current_id):
                raise DuplicateKeyError(
                    f"{self.id_field}={current_id} đã tồn tại trong {self.file_path.name}"
                )

            # Thêm vào chỉ mục chính (O(log N))
            stored_record = copy.copy(record)
            self._primary_index.insert(current_id, stored_record)

            # Thêm vào các chỉ mục phụ (O(log N))
            for field_name in self._indexed_fields:
                val = getattr(stored_record, field_name)
                self._secondary_indices[field_name].insert(val, stored_record)

            # Ghi đĩa đồng bộ (Write-Through)
            self._write_all(self._primary_index.inorder())
            self._last_mtime = self.file_path.stat().st_mtime
            return record

    def update(self, record: T) -> T:
        """Ghi đè bản ghi có cùng khóa chính bằng dữ liệu mới.

        Tìm kiếm và cập nhật Cây AVL với O(log N), sau đó ghi đồng bộ xuống file CSV.
        """
        self._validate_record_type(record)
        with self._lock:
            self._ensure_cache_loaded()
            record_id = getattr(record, self.id_field)
            if record_id is None:
                raise ValueError("Không thể cập nhật model chưa có khóa chính")

            existing = self._primary_index.search(record_id)
            if existing is None:
                raise RecordNotFoundError(
                    f"Không tìm thấy {self.id_field}={record_id} trong {self.file_path.name}"
                )

            # Cập nhật các chỉ mục phụ (O(log N))
            stored_record = copy.copy(record)
            for field_name in self._indexed_fields:
                old_val = getattr(existing, field_name)
                new_val = getattr(stored_record, field_name)
                self._secondary_indices[field_name].update_record(
                    old_key=old_val,
                    new_key=new_val,
                    value=stored_record,
                    identifier_func=lambda r: getattr(r, self.id_field),
                )

            # Cập nhật chỉ mục chính (O(log N))
            self._primary_index.update(record_id, stored_record)

            # Ghi đĩa đồng bộ (Write-Through)
            self._write_all(self._primary_index.inorder())
            self._last_mtime = self.file_path.stat().st_mtime
            return record

    def _ensure_cache_loaded(self) -> None:
        """Nạp dữ liệu từ CSV vào cây AVL hoặc làm mới nếu file trên đĩa bị thay đổi."""
        self._ensure_file_exists()
        current_mtime = self.file_path.stat().st_mtime
        if self._is_loaded and self._last_mtime == current_mtime:
            return

        with self.file_path.open("r", encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            self._validate_header(reader.fieldnames)
            records = [
                self._row_to_model(row, line_number)
                for line_number, row in enumerate(reader, start=2)
                if any(value not in (None, "") for value in row.values())
            ]

        self._primary_index.clear()
        for sec_tree in self._secondary_indices.values():
            sec_tree.clear()

        for record in records:
            rec_id = getattr(record, self.id_field)
            if rec_id is not None:
                self._primary_index.insert(rec_id, record)
            for field_name in self._indexed_fields:
                sec_val = getattr(record, field_name)
                self._secondary_indices[field_name].insert(sec_val, record)

        self._last_mtime = self.file_path.stat().st_mtime
        self._is_loaded = True

    def _ensure_file_exists(self) -> None:
        if not self.file_path.is_file():
            raise FileNotFoundError(f"Không tìm thấy file dữ liệu: {self.file_path}")

    def _validate_header(self, header: Optional[list[str]]) -> None:
        actual = tuple(header or ())
        if actual != self._field_names:
            raise CsvSchemaError(
                f"Header của {self.file_path.name} phải là {self._field_names}, "
                f"nhưng nhận được {actual}"
            )

    def _validate_record_type(self, record: T) -> None:
        if not isinstance(record, self.model_class):
            raise TypeError(
                f"Repository {self.file_path.name} chỉ nhận "
                f"{self.model_class.__name__}"
            )

    def _row_to_model(self, row: dict[str, Optional[str]], line_number: int) -> T:
        if None in row:
            raise CsvSchemaError(
                f"Dòng {line_number} của {self.file_path.name} có nhiều cột hơn header"
            )

        try:
            values = {
                name: self._deserialize(row.get(name, ""), self._type_hints[name])
                for name in self._field_names
            }
            return self.model_class(**values)
        except (TypeError, ValueError, ArithmeticError) as error:
            raise CsvDataError(
                f"Dữ liệu không hợp lệ tại dòng {line_number} "
                f"của {self.file_path.name}: {error}"
            ) from error

    @classmethod
    def _deserialize(cls, raw_value: Optional[str], annotation: Any) -> Any:
        raw_value = "" if raw_value is None else raw_value
        nullable, target_type = cls._unwrap_optional(annotation)

        if raw_value == "" and nullable:
            return None
        if target_type is str:
            return raw_value
        if target_type is int:
            return int(raw_value)
        if target_type is bool:
            normalized = raw_value.strip().lower()
            if normalized in {"1", "true"}:
                return True
            if normalized in {"0", "false"}:
                return False
            raise ValueError(f"{raw_value!r} không phải giá trị bit hợp lệ")
        if target_type is datetime:
            return datetime.fromisoformat(raw_value)
        if target_type is Decimal:
            return Decimal(raw_value)

        raise TypeError(f"Kiểu dữ liệu chưa được hỗ trợ: {annotation!r}")

    @staticmethod
    def _unwrap_optional(annotation: Any) -> tuple[bool, Any]:
        origin = get_origin(annotation)
        if origin in (Union, UnionType):
            arguments = get_args(annotation)
            non_none = tuple(item for item in arguments if item is not type(None))
            if len(non_none) == 1 and len(non_none) != len(arguments):
                return True, non_none[0]
        return False, annotation

    @staticmethod
    def _serialize(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, datetime):
            return value.isoformat(sep=" ", timespec="seconds")
        if isinstance(value, Decimal):
            return format(value, "f")
        return str(value)

    def _next_id(self) -> int:
        """Tìm ID kế tiếp lớn nhất từ Cây AVL với O(log N)."""
        max_id = self._primary_index.max_key()
        return (max_id if max_id is not None else 0) + 1

    def _write_all(self, records: list[T]) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.file_path.stem}_",
            suffix=".tmp",
            dir=self.file_path.parent,
        )
        temporary_path = Path(temporary_name)

        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=self._field_names)
                writer.writeheader()
                for record in records:
                    self._validate_record_type(record)
                    writer.writerow(
                        {
                            name: self._serialize(getattr(record, name))
                            for name in self._field_names
                        }
                    )
                file.flush()
                os.fsync(file.fileno())

            os.replace(temporary_path, self.file_path)
        finally:
            temporary_path.unlink(missing_ok=True)


_DEFAULT_REPOSITORY_CONFIG: dict[str, tuple[type[Any], str, str, tuple[str, ...]]] = {
    "decks": (Deck, "decks.csv", "deck_id", ()),
    "cards": (Card, "cards.csv", "card_id", ("deck_id",)),
    "quizzes": (Quiz, "quizzes.csv", "quiz_id", ("source_deck_id",)),
    "questions": (Question, "questions.csv", "question_id", ("quiz_id",)),
    "quiz_attempts": (QuizAttempt, "quiz_attempts.csv", "attempt_id", ("quiz_id",)),
    "quiz_answers": (QuizAnswer, "quiz_answers.csv", "answer_id", ("attempt_id",)),
}


def create_repositories(
    data_directory: str | Path = DATA_DIR,
) -> dict[str, CsvRepository[Any]]:
    """Tạo repository cho đúng 6 bảng dữ liệu của ứng dụng kèm chỉ mục AVL."""

    directory = Path(data_directory)
    return {
        name: CsvRepository(
            directory / filename,
            model_class,
            id_field,
            indexed_fields=indices,
        )
        for name, (model_class, filename, id_field, indices) in _DEFAULT_REPOSITORY_CONFIG.items()
    }
