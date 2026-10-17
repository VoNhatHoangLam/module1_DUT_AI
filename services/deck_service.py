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

    def get_deck_by_id(self, deck_id: int) -> Optional[tuple[Deck, list[Card]]]:
        """Tìm kiếm bộ thẻ theo khóa chính ID kèm danh sách các thẻ con với độ phức tạp O(log N).

        Sử dụng chỉ mục chính cây AVL (AVLTree) trong CsvRepository để tìm Deck,
        và chỉ mục phụ MultiAVLTree trên trường deck_id để lấy danh sách thẻ.

        Args:
            deck_id: ID của bộ thẻ cần tìm.

        Returns:
            Tuple (Deck, list[Card]) nếu tìm thấy và chưa bị xóa, ngược lại trả về None.
        """
        deck = self.deck_repository.get_by_id(deck_id)
        if deck is None or deck.is_deleted:
            return None
        cards = self.card_repository.find_by(deck_id=deck_id)
        cards.sort(key=lambda c: c.position)
        return (deck, cards)

    def get_decks(
        self,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> dict[str, Any]:
        """Lấy danh sách bộ thẻ hoặc tìm kiếm theo chuỗi tiêu đề có phân trang (tối đa 10 deck/trang).

        Chỉ tìm kiếm theo chuỗi con (substring, case-insensitive) trong tiêu đề bộ thẻ,
        không tìm kiếm theo ID. Không trả về danh sách thẻ (cards) của bộ thẻ.

        Args:
            keyword: Từ khóa tìm kiếm chuỗi con trong tiêu đề bộ thẻ (tùy chọn).
            page: Số trang cần lấy (bắt đầu từ 1, mặc định 1).
            page_size: Số lượng bộ thẻ tối đa trên mỗi trang (mặc định 10, trần tối đa 10).

        Returns:
            dict[str, Any]:
                - items: Danh sách tối đa 10 đối tượng Deck của trang hiện tại (không kèm thẻ con).
                - total_pages: Tổng số trang (ceil(total_count / page_size)).
                - page: Trang hiện tại.
                - page_size: Kích thước trang thực tế (tối đa 10).

        Raises:
            TypeError: Khi page hoặc page_size không phải số nguyên, hoặc keyword không phải chuỗi.
        """
        if isinstance(page, bool) or not isinstance(page, int):
            raise TypeError("page phải là số nguyên")
        if isinstance(page_size, bool) or not isinstance(page_size, int):
            raise TypeError("page_size phải là số nguyên")
        if keyword is not None and not isinstance(keyword, str):
            raise TypeError("keyword phải là chuỗi hoặc None")

        actual_page = max(1, page)
        actual_page_size = max(1, min(page_size, 10))

        clean_kw = keyword.strip() if isinstance(keyword, str) and keyword.strip() else None

        # 1. Đếm tổng số deck thỏa mãn bằng phương thức count() của CsvRepository
        total_count = self.deck_repository.count(
            keyword=clean_kw,
            search_field="title",
            is_deleted=False,
        )

        # 2. Tính toán tổng số trang
        total_pages = (
            (total_count + actual_page_size - 1) // actual_page_size
            if total_count > 0
            else 0
        )

        # 3. Lấy dữ liệu của trang hiện tại (tối đa 10 deck)
        if actual_page > total_pages or total_count == 0:
            paged_decks = []
        else:
            matched = self.deck_repository.find_by_keyword(
                keyword=clean_kw,
                search_field="title",
                is_deleted=False,
            )
            start_idx = (actual_page - 1) * actual_page_size
            end_idx = start_idx + actual_page_size
            paged_decks = matched[start_idx:end_idx]

        return {
            "items": paged_decks,
            "total_pages": total_pages,
            "page": actual_page,
            "page_size": actual_page_size,
        }

