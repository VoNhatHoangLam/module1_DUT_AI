"""Tầng lưu trữ dữ liệu sử dụng các file CSV."""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import fields, is_dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from threading import RLock
from types import UnionType
from typing import Any, Generic, Optional, TypeVar, Union, get_args, get_origin, get_type_hints

from config import DATA_DIR
from models import (
    AccountStatusLog,
    Card,
    Deck,
    Question,
    Quiz,
    QuizAnswer,
    QuizAttempt,
    StudyReview,
    StudySession,
    User,
)


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
    """Thực hiện các thao tác lưu trữ chung cho một dataclass và một file CSV."""

    def __init__(self, file_path: str | Path, model_class: type[T], id_field: str):
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

    def get_all(self) -> list[T]:
        """Đọc toàn bộ bản ghi và chuyển từng dòng thành model."""

        with self._lock:
            self._ensure_file_exists()
            with self.file_path.open("r", encoding="utf-8-sig", newline="") as file:
                reader = csv.DictReader(file)
                self._validate_header(reader.fieldnames)
                return [
                    self._row_to_model(row, line_number)
                    for line_number, row in enumerate(reader, start=2)
                    if any(value not in (None, "") for value in row.values())
                ]

    def get_by_id(self, record_id: int) -> Optional[T]:
        """Tìm một bản ghi theo khóa chính; trả về None nếu không tồn tại."""

        return next(
            (
                record
                for record in self.get_all()
                if getattr(record, self.id_field) == record_id
            ),
            None,
        )

    def find_by(self, **criteria: Any) -> list[T]:
        """Tìm các bản ghi có tất cả trường khớp với điều kiện truyền vào."""

        unknown_fields = set(criteria) - set(self._field_names)
        if unknown_fields:
            names = ", ".join(sorted(unknown_fields))
            raise ValueError(f"Model không có trường: {names}")

        return [
            record
            for record in self.get_all()
            if all(getattr(record, name) == value for name, value in criteria.items())
        ]

    def exists(self, record_id: int) -> bool:
        """Kiểm tra một khóa chính có tồn tại hay không."""

        return self.get_by_id(record_id) is not None

    def add(self, record: T) -> T:
        """Thêm bản ghi, tự cấp khóa chính nếu model chưa có ID."""

        self._validate_record_type(record)
        with self._lock:
            records = self.get_all()
            current_id = getattr(record, self.id_field)

            if current_id is None:
                current_id = self._next_id(records)
                setattr(record, self.id_field, current_id)
            elif any(
                getattr(existing, self.id_field) == current_id for existing in records
            ):
                raise DuplicateKeyError(
                    f"{self.id_field}={current_id} đã tồn tại trong {self.file_path.name}"
                )

            records.append(record)
            self._write_all(records)
            return record

    def update(self, record: T) -> T:
        """Ghi đè bản ghi có cùng khóa chính bằng dữ liệu mới."""

        self._validate_record_type(record)
        with self._lock:
            records = self.get_all()
            record_id = getattr(record, self.id_field)
            if record_id is None:
                raise ValueError("Không thể cập nhật model chưa có khóa chính")

            for index, existing in enumerate(records):
                if getattr(existing, self.id_field) == record_id:
                    records[index] = record
                    self._write_all(records)
                    return record

            raise RecordNotFoundError(
                f"Không tìm thấy {self.id_field}={record_id} trong {self.file_path.name}"
            )

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

    def _next_id(self, records: list[T]) -> int:
        ids = [getattr(record, self.id_field) for record in records]
        return max((record_id for record_id in ids if record_id is not None), default=0) + 1

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


_DEFAULT_REPOSITORY_CONFIG: dict[str, tuple[type[Any], str, str]] = {
    "users": (User, "users.csv", "user_id"),
    "decks": (Deck, "decks.csv", "deck_id"),
    "cards": (Card, "cards.csv", "card_id"),
    "quizzes": (Quiz, "quizzes.csv", "quiz_id"),
    "questions": (Question, "questions.csv", "question_id"),
    "study_sessions": (StudySession, "study_sessions.csv", "study_session_id"),
    "study_reviews": (StudyReview, "study_reviews.csv", "study_review_id"),
    "quiz_attempts": (QuizAttempt, "quiz_attempts.csv", "attempt_id"),
    "quiz_answers": (QuizAnswer, "quiz_answers.csv", "answer_id"),
    "account_status_logs": (
        AccountStatusLog,
        "account_status_logs.csv",
        "status_change_id",
    ),
}


def create_repositories(
    data_directory: str | Path = DATA_DIR,
) -> dict[str, CsvRepository[Any]]:
    """Tạo repository cho đúng 10 bảng dữ liệu của ứng dụng."""

    directory = Path(data_directory)
    return {
        name: CsvRepository(directory / filename, model_class, id_field)
        for name, (model_class, filename, id_field) in _DEFAULT_REPOSITORY_CONFIG.items()
    }
