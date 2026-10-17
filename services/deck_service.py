"""Nghiệp vụ quản lý bộ thẻ (Deck)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from config import DATA_DIR
from models import Card, Deck
from repositories import CsvRepository


class DeckService:
    """Lớp nghiệp vụ quản lý bộ thẻ."""

    def __init__(
        self,
        deck_repository: Optional[CsvRepository[Deck]] = None,
        card_repository: Optional[CsvRepository[Card]] = None,
    ) -> None:
        self.deck_repository = deck_repository or CsvRepository(
            DATA_DIR / "decks.csv", Deck, "deck_id"
        )
        self.card_repository = card_repository or CsvRepository(
            DATA_DIR / "cards.csv", Card, "card_id", indexed_fields=("deck_id",)
        )

    def create_deck(
        self,
        title: str,
        cards: list[dict[str, Any]],
        description: Optional[str] = None
    ) -> tuple[int, str, Optional[str], datetime, int]:
        """Thêm 1 bản ghi bộ thẻ mới vào file data/decks.csv và các thẻ vào data/cards.csv.

        Khởi tạo đối tượng Deck và gọi phương thức add() của CsvRepository
        để tự động cấp phát khóa chính (deck_id) và lưu dữ liệu an toàn xuống file CSV.
        Mỗi thẻ trong danh sách cards được lưu vào cards.csv kèm deck_id tương ứng.

        Args:
            title: Tiêu đề của bộ thẻ (bắt buộc, không được để trống).
            description: Mô tả chi tiết của bộ thẻ (tuỳ chọn).
            cards: Danh sách các dict chứa thông tin thẻ (front_text, back_text, position).
                   Bắt buộc truyền danh sách, không được là None.

        Returns:
            tuple gồm (deck_id, title, description, updated_at, card_count).

        Raises:
            ValueError: Khi title để trống hoặc cards là None.
            TypeError: Khi cards không phải là list.
        """
        # Xác thực tham số cards bắt buộc
        if cards is None:
            raise ValueError("Tham số cards là bắt buộc, không được là None")
        if not isinstance(cards, list):
            raise TypeError("Tham số cards phải là một danh sách (list)")

        # Xác thực tiêu đề title bắt buộc
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Tiêu đề bộ thẻ không được để trống")

        clean_title = title.strip()
        clean_description = (
            description.strip() if isinstance(description, str) and description.strip() else None
        )

        # Tạo thực thể Deck mới (không truyền deck_id để add() tự sinh ID mới O(log N))
        new_deck = Deck(
            title=clean_title,
            description=clean_description,
            total_cards=len(cards),
        )

        # Gọi hàm add trong csv_repository.py để lưu vào decks.csv (O(log N))
        saved_deck = self.deck_repository.add(new_deck)

        # Thêm từng thẻ vào data/cards.csv (O(log N) trên cả primary và secondary AVL tree)
        for idx, card_data in enumerate(cards, start=1):
            if not isinstance(card_data, dict):
                raise TypeError("Mỗi phần tử trong cards phải là một dictionary")
            card = Card(
                deck_id=saved_deck.deck_id,
                front_text=str(card_data.get("front_text", "")).strip(),
                back_text=str(card_data.get("back_text", "")).strip(),
                position=int(card_data.get("position", idx)),
            )
            self.card_repository.add(card)

        card_count = len(cards)

        return (
            saved_deck.deck_id,
            saved_deck.title,
            saved_deck.description,
            saved_deck.updated_at,
            card_count
        )
