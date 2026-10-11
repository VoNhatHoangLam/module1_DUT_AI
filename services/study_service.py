"""Nghiệp vụ học flashcard theo cơ chế hàng đợi."""

from __future__ import annotations

from typing import Iterable, Optional

from models import Card
from utils import Queue


class NoCardToReviewError(LookupError):
    """Phiên học không còn thẻ để ôn tập."""


class FlashcardStudyQueue:
    """Quản lý thứ tự thẻ trong một phiên học bằng hàng đợi FIFO.

    Thẻ đã thuộc bị loại khỏi hàng đợi. Thẻ chưa thuộc được đưa xuống
    cuối hàng đợi và sẽ xuất hiện lại sau các thẻ đang chờ khác.
    """

    def __init__(self, cards: Iterable[Card]) -> None:
        ordered_cards = sorted(cards, key=lambda card: card.position)
        self._cards: Queue[Card] = Queue(ordered_cards)

    @property
    def current_card(self) -> Optional[Card]:
        """Thẻ hiện tại hoặc None nếu phiên học đã hoàn thành."""

        if self._cards.is_empty():
            return None
        return self._cards.peek()

    @property
    def remaining_count(self) -> int:
        """Số thẻ vẫn còn trong hàng đợi."""

        return len(self._cards)

    @property
    def is_completed(self) -> bool:
        """Cho biết người học đã đánh dấu thuộc tất cả thẻ hay chưa."""

        return self._cards.is_empty()

    def mark_known(self) -> Card:
        """Đánh dấu đã thuộc và loại thẻ hiện tại khỏi hàng đợi."""

        self._ensure_card_available()
        return self._cards.dequeue()

    def mark_unknown(self) -> Card:
        """Đánh dấu chưa thuộc và đưa thẻ hiện tại xuống cuối hàng đợi."""

        self._ensure_card_available()
        card = self._cards.dequeue()
        self._cards.enqueue(card)
        return card

    def review_current_card(self, is_known: bool) -> Card:
        """Xử lý lựa chọn thuộc/chưa thuộc của người học."""

        if not isinstance(is_known, bool):
            raise TypeError("is_known phải là True hoặc False")
        return self.mark_known() if is_known else self.mark_unknown()

    def _ensure_card_available(self) -> None:
        if self._cards.is_empty():
            raise NoCardToReviewError("Phiên học không còn thẻ để ôn tập")
