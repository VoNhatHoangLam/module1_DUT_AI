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
            DATA_DIR / "cards.csv", Card, "card_id"
        )

    def create_deck(
        self,
        title: str,
        description: Optional[str] = None,
        cards: Optional[list[dict[str, Any]]] = None,
    ) -> tuple[int, str, Optional[str], datetime, int, list[Card]]:
        """Thêm 1 bản ghi bộ thẻ mới vào file data/decks.csv và các thẻ vào data/cards.csv.

        Khởi tạo đối tượng Deck và gọi phương thức add() của CsvRepository
        để tự động cấp phát khóa chính (deck_id) và lưu dữ liệu an toàn xuống file CSV.
        Nếu danh sách cards được cung cấp, từng thẻ sẽ được thêm vào cards.csv.

        Args:
            title: Tiêu đề của bộ thẻ.
            description: Mô tả chi tiết của bộ thẻ (tuỳ chọn).
            cards: Danh sách các dict chứa thông tin thẻ (front_text, back_text, position).

        Returns:
            tuple gồm (deck_id, title, description, updated_at, số_thẻ_trong_deck, danh_sách_thẻ).
        """
        card_items = cards or []

        # Tạo thực thể Deck mới (không truyền deck_id để add() tự sinh ID mới)
        new_deck = Deck(
            title=title.strip() if isinstance(title, str) else str(title),
            description=description.strip() if isinstance(description, str) else description,
            total_cards=len(card_items),
            is_studied=False,
        )

        # Gọi hàm add trong csv_repository.py để lưu vào decks.csv
        saved_deck = self.deck_repository.add(new_deck)

        # Thêm từng thẻ vào data/cards.csv nếu có
        saved_cards: list[Card] = []
        for idx, card_data in enumerate(card_items, start=1):
            card = Card(
                deck_id=saved_deck.deck_id,
                front_text=str(card_data.get("front_text", "")),
                back_text=str(card_data.get("back_text", "")),
                position=int(card_data.get("position", idx)),
            )
            saved_cards.append(self.card_repository.add(card))

        card_count = len(saved_cards)

        return (
            saved_deck.deck_id,
            saved_deck.title,
            saved_deck.description,
            saved_deck.updated_at,
            card_count,
            saved_cards,
        )
