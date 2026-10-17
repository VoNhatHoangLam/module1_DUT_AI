"""Nghiệp vụ quản lý bộ thẻ (Deck)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from config import DATA_DIR
from models import Card, Deck
from repositories import CsvRepository, RecordNotFoundError
from utils import CsvImporter


class DeckService:
    """Lớp nghiệp vụ quản lý bộ thẻ.

    Tương tác với tầng lưu trữ CsvRepository tích hợp Cây AVL (AVLTree & MultiAVLTree) để:
    - Tìm kiếm bộ thẻ theo ID với độ phức tạp O(log N).
    - Tìm kiếm bộ thẻ theo Tiêu đề (Title) với độ phức tạp O(log N).
    - Tìm kiếm bộ thẻ theo Tiền tố (Prefix) với độ phức tạp O(log N + K).
    - Duyệt toàn bộ danh sách bộ thẻ từ bộ nhớ RAM theo thứ tự tăng dần.
    - Đọc và xác thực dữ liệu thẻ từ file CSV bằng CsvImporter (không tự động lưu).
    """

    def __init__(
        self,
        deck_repository: Optional[CsvRepository[Deck]] = None,
        card_repository: Optional[CsvRepository[Card]] = None,
        csv_importer: Optional[CsvImporter] = None,
    ) -> None:
        self.deck_repository = deck_repository or CsvRepository(
            DATA_DIR / "decks.csv", Deck, "deck_id", indexed_fields=("title",)
        )
        self.card_repository = card_repository or CsvRepository(
            DATA_DIR / "cards.csv", Card, "card_id", indexed_fields=("deck_id",)
        )
        self.csv_importer = csv_importer or CsvImporter()

    def import_cards_from_csv(
        self,
        source: Any,
    ) -> list[dict[str, Any]]:
        """Đọc và kiểm tra file CSV, chuẩn hóa danh sách thẻ để điền vào giao diện tạo Deck.

        QUAN TRỌNG: Hàm này chỉ phân tích cú pháp và trả về danh sách thẻ,
        KHÔNG tự động tạo hay lưu Deck vào hệ thống. Người dùng phải xác nhận
        và gọi phương thức create_deck() sau đó.

        Args:
            source: Đường dẫn file CSV, đối tượng file text hoặc chuỗi văn bản CSV.

        Returns:
            Danh sách các dict chứa front_text, back_text, position.
        """
        return self.csv_importer.import_cards(source)

    def create_deck(
        self,
        title: str,
        cards: list[dict[str, Any]],
        description: Optional[str] = None,
    ) -> tuple[int, str, Optional[str], int]:
        """Thêm 1 bản ghi bộ thẻ mới vào file data/decks.csv và các thẻ vào data/cards.csv.

        Khởi tạo đối tượng Deck và gọi phương thức add() của CsvRepository
        để tự động cấp phát khóa chính (deck_id) và lưu dữ liệu an toàn xuống file CSV.
        Mỗi thẻ trong danh sách cards được lưu vào cards.csv kèm deck_id tương ứng.

        Args:
            title: Tiêu đề của bộ thẻ (bắt buộc, không được để trống).
            cards: Danh sách các dict chứa thông tin thẻ (front_text, back_text, position).
                   Bắt buộc truyền danh sách, không được là None.
            description: Mô tả chi tiết của bộ thẻ (tuỳ chọn).

        Returns:
            tuple gồm (deck_id, title, description, card_count).

        Raises:
            ValueError: Khi title để trống hoặc cards là None.
            TypeError: Khi cards không phải là list hoặc có phần tử không phải dict.
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

        # Tạo thực thể Deck mới (không truyền deck_id để add() tự sinh ID mới)
        new_deck = Deck(
            title=clean_title,
            description=clean_description,
            total_cards=len(cards),
            is_studied=False,
            is_deleted=False,
        )

        # Lưu vào decks.csv (O(log N) trên cây AVL và ghi atomic xuống đĩa, tự động cập nhật chỉ mục phụ)
        saved_deck = self.deck_repository.add(new_deck)

        # Thêm từng thẻ vào data/cards.csv (O(log N) trên cả primary và secondary AVL tree)
        for idx, card_data in enumerate(cards, start=1):
            if not isinstance(card_data, dict):
                raise TypeError("Mỗi phần tử trong cards phải là một dictionary")
            front_text = str(card_data.get("front_text", card_data.get("term", ""))).strip()
            back_text = str(card_data.get("back_text", card_data.get("definition", ""))).strip()
            position = int(card_data.get("position", idx))
            card = Card(
                deck_id=saved_deck.deck_id,
                front_text=front_text,
                back_text=back_text,
                position=position,
            )
            self.card_repository.add(card)

        card_count = len(cards)

        return (
            saved_deck.deck_id,
            saved_deck.title,
            saved_deck.description,
            card_count,
        )

    def delete_deck(
        self,
        deck_id: int,
    ) -> bool:
        """Xóa vĩnh viễn bộ thẻ khỏi decks.csv và xóa liên hoàn (Cascade Delete) các thẻ con trong cards.csv.

        Kiểm tra sự tồn tại của bộ thẻ bằng phương thức exists() ở tầng repository với O(log N).
        Nếu không tìm thấy, trả về False.
        Nếu tìm thấy, xóa toàn bộ các thẻ liên kết trong cards.csv, sau đó xóa bộ thẻ khỏi decks.csv và trả về True.

        Args:
            deck_id: Khóa chính định danh bộ thẻ cần xóa.

        Returns:
            True nếu xóa thành công, False nếu không tìm thấy bộ thẻ với ID tương ứng.
        """
        if not self.deck_repository.exists(deck_id):
            return False

        # Xóa liên hoàn các thẻ con thuộc deck_id trong cards.csv (Cascade Delete)
        associated_cards = self.card_repository.find_by(deck_id=deck_id)
        for card in associated_cards:
            if card.card_id is not None:
                self.card_repository.delete(card.card_id)

        # Xóa vĩnh viễn bộ thẻ khỏi decks.csv
        return self.deck_repository.delete(deck_id)

    def get_deck_by_id(self, deck_id: int) -> Optional[Deck]:
        """Tìm kiếm bộ thẻ theo khóa chính ID với độ phức tạp O(log N).

        Sử dụng trực tiếp chỉ mục chính cây AVL (AVLTree) trong CsvRepository.

        Args:
            deck_id: ID của bộ thẻ cần tìm.

        Returns:
            Đối tượng Deck nếu tìm thấy và chưa bị xóa, ngược lại trả về None.
        """
        deck = self.deck_repository.get_by_id(deck_id)
        if deck is None or deck.is_deleted:
            return None
        return deck

    def get_all_decks(self) -> list[Deck]:
        """Lấy toàn bộ danh sách bộ thẻ hiện có trong hệ thống (chưa bị xóa).

        Duyệt In-order trên Cây AVL trong bộ nhớ RAM với độ phức tạp O(N).

        Returns:
            Danh sách các đối tượng Deck hợp lệ (is_deleted=False).
        """
        return [d for d in self.deck_repository.get_all() if not d.is_deleted]

    def search_deck_by_title(self, title: str) -> list[Deck]:
        """Tìm kiếm bộ thẻ chính xác theo tiêu đề với độ phức tạp O(log N).

        Sử dụng Cây MultiAVLTree (Title Index) quản lý trong CsvRepository.

        Args:
            title: Tiêu đề bộ thẻ cần tìm.

        Returns:
            Danh sách các bộ thẻ có tiêu đề khớp hoàn toàn (chưa bị xóa).
        """
        matched = self.deck_repository.find_by(title=title.strip())
        return [d for d in matched if not d.is_deleted]

    def search_decks_by_title_prefix(self, prefix: str) -> list[Deck]:
        """Tìm kiếm các bộ thẻ có tiêu đề bắt đầu bằng prefix với độ phức tạp O(log N + K).

        Định vị nhánh cây AVL trong O(log N) và thu thập K kết quả khớp tiền tố trong O(K) thông qua CsvRepository.

        Args:
            prefix: Tiền tố tiêu đề cần tìm kiếm.

        Returns:
            Danh sách các bộ thẻ có tiêu đề bắt đầu bằng tiền tố (chưa bị xóa).
        """
        matched = self.deck_repository.find_by_prefix("title", prefix.strip())
        return [d for d in matched if not d.is_deleted]

    def search_decks(self, query: str | int) -> list[Deck]:
        """Tìm kiếm bộ thẻ linh hoạt theo ID hoặc Tiêu đề với độ phức tạp O(log N).

        - Nếu query là số: tìm theo deck_id bằng cây AVL chính với O(log N).
        - Nếu query là chuỗi: tìm theo tiêu đề chính xác O(log N), hoặc tiền tố O(log N + K).

        Args:
            query: Từ khóa tìm kiếm (chuỗi hoặc số nguyên ID).

        Returns:
            Danh sách các bộ thẻ khớp điều kiện tìm kiếm.
        """
        if isinstance(query, int):
            found = self.get_deck_by_id(query)
            return [found] if found is not None else []

        q_str = str(query).strip()
        if not q_str:
            return self.get_all_decks()

        if q_str.isdigit():
            found = self.get_deck_by_id(int(q_str))
            if found is not None:
                return [found]

        # Tìm kiếm chính xác tiêu đề trước (O(log N))
        exact_matches = self.search_deck_by_title(q_str)
        if exact_matches:
            return exact_matches

        # Tìm kiếm theo tiền tố tiêu đề (O(log N + K))
        return self.search_decks_by_title_prefix(q_str)

    def get_cards_by_deck_id(self, deck_id: int) -> list[Card]:
        """Lấy tất cả các thẻ của một bộ thẻ với độ phức tạp O(log N).

        Tận dụng chỉ mục phụ `deck_id` của CsvRepository[Card].
        """
        cards = self.card_repository.find_by(deck_id=deck_id)
        cards.sort(key=lambda c: c.position)
        return cards
