"""Nghiệp vụ học flashcard theo cơ chế hàng đợi hai giai đoạn chuẩn FIFO."""

from __future__ import annotations

from typing import Iterable, Optional

from models import Card
from utils import Queue


class NoCardToReviewError(LookupError):
    """Phiên học không còn thẻ để ôn tập."""


class FlashcardStudyQueue:
    """Quản lý tiến trình học flashcard bằng cơ chế hàng đợi hai giai đoạn.

    Giai đoạn 1 (Initial Pass - Duyệt thẻ ban đầu):
        Duyệt qua danh sách thẻ ban đầu theo thứ tự position.
        - Nếu đánh dấu chưa thuộc: Thêm thẻ vào CUỐI queue (enqueue).
        - Nếu đánh dấu đã thuộc: Không thêm vào queue.

    Giai đoạn 2 (Queue Review - Ôn tập thẻ chưa thuộc):
        Bắt đầu khi tất cả thẻ ban đầu đã được xem qua và đánh dấu.
        - Lấy thẻ ở ĐẦU queue (peek / dequeue) để hiển thị ôn tập theo đúng thứ tự FIFO.
        - Nếu đánh dấu chưa thuộc: Tiếp tục đưa lại vào CUỐI queue (enqueue).
        - Nếu đánh dấu đã thuộc: Loại khỏi queue (thẻ đã thuộc).

    Phiên học hoàn thành khi tất cả thẻ ban đầu đã duyệt qua và queue hoàn toàn rỗng.
    """

    def __init__(self, cards: Iterable[Card]) -> None:
        ordered_cards = sorted(cards, key=lambda card: card.position)
        self._initial_cards: list[Card] = ordered_cards
        self._initial_index: int = 0
        self._unknown_queue: Queue[Card] = Queue()
        self._known_cards: list[Card] = []
        self._total_cards: int = len(self._initial_cards)

    @property
    def current_card(self) -> Optional[Card]:
        """Thẻ hiện tại đang chờ người học đánh dấu, hoặc None nếu đã hoàn thành."""
        if self._initial_index < len(self._initial_cards):
            return self._initial_cards[self._initial_index]
        if not self._unknown_queue.is_empty():
            return self._unknown_queue.peek()
        return None

    @property
    def is_initial_phase(self) -> bool:
        """Cho biết phiên học có đang ở giai đoạn duyệt thẻ ban đầu hay không."""
        return self._initial_index < len(self._initial_cards)

    @property
    def remaining_count(self) -> int:
        """Tổng số lượt thẻ còn cần xem hoặc ôn tập tiếp."""
        initial_remaining = max(0, len(self._initial_cards) - self._initial_index)
        return initial_remaining + len(self._unknown_queue)

    @property
    def unknown_count(self) -> int:
        """Số lượng thẻ hiện đang nằm trong hàng đợi."""
        return len(self._unknown_queue)

    @property
    def known_count(self) -> int:
        """Số lượng thẻ đã học thuộc thành công."""
        return len(self._known_cards)

    @property
    def total_cards(self) -> int:
        """Tổng số thẻ ban đầu của phiên học."""
        return self._total_cards

    @property
    def is_completed(self) -> bool:
        """Cho biết người học đã đánh dấu thuộc tất cả các thẻ hay chưa."""
        return (
            self._initial_index >= len(self._initial_cards)
            and self._unknown_queue.is_empty()
        )

    def mark_card(self, is_known: bool) -> Card:
        """Đánh dấu thẻ hiện tại là đã thuộc (True) hoặc chưa thuộc (False).

        Args:
            is_known: True nếu đã thuộc, False nếu chưa thuộc.

        Returns:
            Thẻ vừa được đánh dấu.

        Raises:
            TypeError: Khi is_known không phải kiểu boolean (True/False).
            NoCardToReviewError: Khi phiên học đã hoàn thành, không còn thẻ để đánh dấu.
        """
        if not isinstance(is_known, bool):
            raise TypeError("is_known phải là True hoặc False")

        self._ensure_card_available()

        # Giai đoạn 1: Duyệt qua các thẻ ban đầu
        if self._initial_index < len(self._initial_cards):
            card = self._initial_cards[self._initial_index]
            self._initial_index += 1

            if is_known:
                self._known_cards.append(card)
            else:
                # Đánh dấu chưa thuộc -> thêm vào cuối queue chuẩn FIFO
                self._unknown_queue.enqueue(card)
            return card

        # Giai đoạn 2: Lấy thẻ ở đầu queue để hiển thị ôn tập
        card = self._unknown_queue.dequeue()

        if is_known:
            self._known_cards.append(card)
        else:
            # Nếu người dùng vẫn đánh dấu chưa thuộc, đưa lại vào cuối queue
            self._unknown_queue.enqueue(card)

        return card

    def mark_known(self) -> Card:
        """Đánh dấu đã thuộc cho thẻ hiện tại."""
        return self.mark_card(True)

    def mark_unknown(self) -> Card:
        """Đánh dấu chưa thuộc cho thẻ hiện tại."""
        return self.mark_card(False)

    def review_current_card(self, is_known: bool) -> Card:
        """Alias tương thích ngược: Xử lý lựa chọn thuộc/chưa thuộc của người học."""
        return self.mark_card(is_known)

    def _ensure_card_available(self) -> None:
        """Xác nhận phiên học vẫn còn thẻ để thao tác."""
        if self.is_completed:
            raise NoCardToReviewError("Phiên học không còn thẻ để ôn tập")
