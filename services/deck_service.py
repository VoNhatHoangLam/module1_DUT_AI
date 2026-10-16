"""Nghiệp vụ quản lý bộ thẻ (Deck)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from config import DATA_DIR
from models import Card, Deck
from repositories import CsvRepository, RecordNotFoundError
from utils import CsvImporter, MultiAVLTree


class DeckService:
    """Lớp nghiệp vụ quản lý bộ thẻ.

    Tích hợp Cấu trúc Dữ liệu Cây AVL (AVLTree & MultiAVLTree) để:
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
            DATA_DIR / "decks.csv", Deck, "deck_id"
        )
        self.card_repository = card_repository or CsvRepository(
            DATA_DIR / "cards.csv", Card, "card_id", indexed_fields=("deck_id",)
        )
        self.csv_importer = csv_importer or CsvImporter()
        # Chỉ mục phụ tiêu đề (Title Index) sử dụng MultiAVLTree để tìm kiếm O(log N)
        self._title_index: MultiAVLTree[str, Deck] = MultiAVLTree()
        self._rebuild_title_index()

    def _rebuild_title_index(self) -> None:
        """Đồng bộ chỉ mục tiêu đề từ repository vào cây MultiAVLTree."""
        self._title_index.clear()
        for deck in self.deck_repository.get_all():
            if not deck.is_deleted:
                self._title_index.insert(deck.title, deck)

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
        description: Optional[str] = None,
        cards: Optional[list[dict[str, Any]]] = None,
    ) -> tuple[int, str, Optional[str], datetime, int, list[Card]]:
        """Thêm 1 bản ghi bộ thẻ mới vào file data/decks.csv và các thẻ vào data/cards.csv.

        Khởi tạo đối tượng Deck và gọi phương thức add() của CsvRepository
        để tự động cấp phát khóa chính (deck_id) và lưu dữ liệu an toàn xuống file CSV.
        Nếu danh sách cards được cung cấp, từng thẻ sẽ được thêm vào cards.csv.

        Args:
            title: Tiêu đề của bộ thẻ (bắt buộc, không được để trống).
            description: Mô tả chi tiết của bộ thẻ (tuỳ chọn).
            cards: Danh sách các dict chứa thông tin thẻ (front_text, back_text, position).

        Returns:
            tuple gồm (deck_id, title, description, updated_at, số_thẻ_trong_deck, danh_sách_thẻ).

        Raises:
            ValueError: Nếu tiêu đề bộ thẻ bị rỗng hoặc chỉ toàn khoảng trắng.
        """
        if not isinstance(title, str) or not title.strip():
            raise ValueError("Tiêu đề bộ thẻ không được để trống")

        card_items = cards or []

        # Tạo thực thể Deck mới (không truyền deck_id để add() tự sinh ID mới)
        new_deck = Deck(
            title=title.strip(),
            description=description.strip() if isinstance(description, str) and description.strip() else description,
            total_cards=len(card_items),
            is_studied=False,
            is_deleted=False,
        )

        # Lưu vào decks.csv (O(log N) trên cây AVL và ghi atomic xuống đĩa)
        saved_deck = self.deck_repository.add(new_deck)

        # Cập nhật chỉ mục tiêu đề
        self._title_index.insert(saved_deck.title, saved_deck)

        # Thêm từng thẻ vào data/cards.csv nếu có
        saved_cards: list[Card] = []
        for idx, card_data in enumerate(card_items, start=1):
            front_text = str(card_data.get("front_text", card_data.get("term", ""))).strip()
            back_text = str(card_data.get("back_text", card_data.get("definition", ""))).strip()
            position = int(card_data.get("position", idx))
            card = Card(
                deck_id=saved_deck.deck_id,
                front_text=front_text,
                back_text=back_text,
                position=position,
            )
            saved_cards.append(self.card_repository.add(card))

        return (
            saved_deck.deck_id,
            saved_deck.title,
            saved_deck.description,
            saved_deck.updated_at,
            len(saved_cards),
            saved_cards,
        )

    def delete_deck(
        self,
        deck_id: int,
        user_id: Optional[str] = None,
        hard_delete: bool = False,
    ) -> bool:
        """Xóa bộ thẻ theo đúng cơ chế Soft Delete của hệ thống và quyền hạn.

        Args:
            deck_id: Khóa chính định danh bộ thẻ cần xóa.
            user_id: ID của người dùng thực hiện xóa (kiểm tra quyền nếu áp dụng).
            hard_delete: Mặc định False (thực hiện Soft Delete cập nhật is_deleted=True).

        Returns:
            True nếu xóa thành công.

        Raises:
            RecordNotFoundError: Nếu không tìm thấy deck_id hoặc bộ thẻ đã bị xóa trước đó.
        """
        existing = self.deck_repository.get_by_id(deck_id)
        if existing is None or existing.is_deleted:
            raise RecordNotFoundError(f"Không tìm thấy bộ thẻ với ID={deck_id}")

        # Cập nhật trạng thái xóa mềm
        existing.is_deleted = True
        existing.updated_at = datetime.now().replace(microsecond=0)

        # Lưu cập nhật vào CsvRepository (O(log N))
        self.deck_repository.update(existing)

        # Xóa khỏi chỉ mục tiêu đề
        self._title_index.remove(
            existing.title,
            existing,
            identifier_func=lambda d: d.deck_id,
        )

        return True

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

        Sử dụng Cây MultiAVLTree (Title Index) trong RAM.

        Args:
            title: Tiêu đề bộ thẻ cần tìm.

        Returns:
            Danh sách các bộ thẻ có tiêu đề khớp hoàn toàn (chưa bị xóa).
        """
        matched = self._title_index.search(title.strip())
        return [d for d in matched if not d.is_deleted]

    def search_decks_by_title_prefix(self, prefix: str) -> list[Deck]:
        """Tìm kiếm các bộ thẻ có tiêu đề bắt đầu bằng prefix với độ phức tạp O(log N + K).

        Định vị nhánh cây AVL trong O(log N) và thu thập K kết quả khớp tiền tố trong O(K).

        Args:
            prefix: Tiền tố tiêu đề cần tìm kiếm.

        Returns:
            Danh sách các bộ thẻ có tiêu đề bắt đầu bằng tiền tố (chưa bị xóa).
        """
        matched = self._title_index.prefix_search(prefix.strip())
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
