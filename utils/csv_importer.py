"""Đọc và kiểm tra file flashcards được tải lên bằng lớp CsvImporter."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, TextIO


class CsvImporter:
    """Lớp xử lý đọc, kiểm tra và chuẩn hóa dữ liệu flashcard từ file CSV.

    Lưu ý kiến trúc: Lớp này chỉ chịu trách nhiệm đọc và xác thực dữ liệu,
    chuẩn hóa thành danh sách thẻ để điền vào form tạo Deck. Tuyệt đối không
    tự ý tạo hay lưu Deck vào cơ sở dữ liệu.
    """

    DEFAULT_FRONT_FIELDS: frozenset[str] = frozenset({
        "front_text", "term", "front", "question", "thuat_ngu", "mat_truoc"
    })
    DEFAULT_BACK_FIELDS: frozenset[str] = frozenset({
        "back_text", "definition", "back", "answer", "dinh_nghia", "mat_sau"
    })

    def __init__(self, encoding: str = "utf-8-sig") -> None:
        """Khởi tạo đối tượng CsvImporter với bảng mã encoding chỉ định."""
        self.encoding = encoding

    def import_cards(self, source: str | Path | TextIO) -> list[dict[str, Any]]:
        """Đọc dữ liệu thẻ từ file hoặc chuỗi CSV và trả về danh sách thẻ chuẩn hóa.

        Dữ liệu được chuẩn hóa thành danh sách dict:
        [
            {"front_text": str, "back_text": str, "position": int},
            ...
        ]

        Hỗ trợ linh hoạt các tiêu đề cột:
        - ('front_text', 'back_text')
        - ('term', 'definition')
        - ('front', 'back')
        - ('question', 'answer')

        Hỗ trợ các dấu phân cách: dấu phẩy (,), dấu chấm phẩy (;), dấu tab (\\t).

        Args:
            source: Đường dẫn file (str hoặc Path), đối tượng file text, hoặc chuỗi văn bản CSV.

        Returns:
            Danh sách các dict chứa front_text, back_text, position (bắt đầu từ 1).

        Raises:
            FileNotFoundError: Nếu source là đường dẫn file nhưng file không tồn tại.
            ValueError: Nếu nội dung rỗng, sai định dạng hoặc không có thẻ hợp lệ.
            TypeError: Nếu source không thuộc kiểu dữ liệu hợp lệ.
        """
        raw_text = self._read_raw_content(source)
        return self._parse_cards_from_text(raw_text)

    def _read_raw_content(self, source: str | Path | TextIO) -> str:
        """Đọc nội dung thô từ file, đường dẫn hoặc đối tượng file text."""
        if hasattr(source, "read"):
            return source.read()  # type: ignore[union-attr]

        if isinstance(source, Path):
            if not source.is_file():
                raise FileNotFoundError(f"Không tìm thấy file: {source}")
            return source.read_text(encoding=self.encoding)

        if isinstance(source, str):
            candidate_path = Path(source)
            if (
                "\n" not in source
                and "\r" not in source
                and (candidate_path.is_file() or candidate_path.suffix.lower() in (".csv", ".txt", ".tsv"))
            ):
                if not candidate_path.is_file():
                    raise FileNotFoundError(f"Không tìm thấy file: {source}")
                return candidate_path.read_text(encoding=self.encoding)
            return source

        raise TypeError(f"Kiểu nguồn không hợp lệ: {type(source).__name__}")

    def _parse_cards_from_text(self, raw_text: str) -> list[dict[str, Any]]:
        """Phân tích chuỗi CSV văn bản thành danh sách thẻ chuẩn hóa."""
        if not raw_text or not raw_text.strip():
            raise ValueError("Nội dung CSV rỗng")

        lines = [line for line in raw_text.splitlines() if line.strip()]
        if not lines:
            raise ValueError("Nội dung CSV không có dòng dữ liệu")

        first_line = lines[0]
        delimiter = ","
        if "\t" in first_line:
            delimiter = "\t"
        elif ";" in first_line and "," not in first_line:
            delimiter = ";"

        reader = csv.reader(lines, delimiter=delimiter)
        all_rows = [row for row in reader if any(cell.strip() for cell in row)]
        if not all_rows:
            raise ValueError("Không tìm thấy dòng dữ liệu hợp lệ trong CSV")

        header_candidates = [col.strip().lower() for col in all_rows[0]]
        has_header = False
        front_idx = 0
        back_idx = 1

        matched_front = next(
            (i for i, col in enumerate(header_candidates) if col in self.DEFAULT_FRONT_FIELDS),
            None,
        )
        matched_back = next(
            (i for i, col in enumerate(header_candidates) if col in self.DEFAULT_BACK_FIELDS),
            None,
        )

        if matched_front is not None and matched_back is not None:
            has_header = True
            front_idx = matched_front
            back_idx = matched_back

        start_idx = 1 if has_header else 0
        data_rows = all_rows[start_idx:]

        cards: list[dict[str, Any]] = []
        for row in data_rows:
            if len(row) <= max(front_idx, back_idx):
                continue
            front = row[front_idx].strip()
            back = row[back_idx].strip()
            if front and back:
                cards.append({
                    "front_text": front,
                    "back_text": back,
                    "position": len(cards) + 1,
                })

        if not cards:
            raise ValueError(
                "Không tìm thấy thẻ hợp lệ nào trong file CSV (yêu cầu ít nhất 2 cột: front_text, back_text)"
            )

        return cards
