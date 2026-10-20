
### 1. "Services tìm theo `title`, Web UI tìm cả 3 trường: Vậy là sai à?"

**Đúng, đây là sự không nhất quán giữa giao diện và nghiệp vụ thuật toán:**

1. **Về mặt bài toán Cấu trúc dữ liệu (Module 1 - Cây AVL):**
   * Đề tài yêu cầu tìm kiếm bộ thẻ với độ phức tạp **$O(\log N)$** (tìm chính xác) hoặc **$O(\log N + K)$** (tìm theo tiền tố - Prefix).
   * Cây chỉ mục phụ `MultiAVLTree` trong [deck_service.py:L31-L33](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/services/deck_service.py#L31-L33) chỉ được dựng riêng cho trường **`title`**:
     ```python
     self.deck_repository = CsvRepository(
         DATA_DIR / "decks.csv", Deck, "deck_id", indexed_fields=("title",)
     )
     ```
   * Cây AVL không thể tìm kiếm trên `description` hay `category` (vì 2 trường này không có chỉ mục cây). Do đó, ở tầng backend, việc tìm kiếm theo cây AVL chỉ có thể áp dụng cho **`title`**.

2. **Vì sao Web UI lại tìm theo cả 3 trường?**
   * Trong [ui/src/components/views/MySetsView.tsx:L44-L50](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/ui/src/components/views/MySetsView.tsx#L44-L50), đây là **code mock tạm thời** từ giai đoạn làm giao diện ban đầu:
     ```typescript
     const matchSearch =
       (s.title || '').toLowerCase().includes(search.toLowerCase()) ||
       (s.description || '').toLowerCase().includes(search.toLowerCase()) ||
       (s.category || '').toLowerCase().includes(search.toLowerCase());
     ```
   * Khi người dùng gõ vào ô tìm kiếm, giao diện **hoàn toàn không gửi API request** nào về backend mà chỉ dùng hàm `.filter()` trên mảng JavaScript có sẵn trong RAM trình duyệt.

---

### 2. Kiểm tra chi tiết luồng tìm kiếm Prefix hiện tại

Luồng tìm kiếm hiện tại bị **đứt gãy ở 3 vị trí**:

```
[Giao diện Web UI]  ──(1. Đứt gãy: Không gọi API)──> [FastAPI main.py]
                                                             │
                                                     (2. Đứt gãy: Dùng chuỗi con O(N),
                                                                 không gọi prefix_search)
                                                             ▼
                                                    [deck_service.py]
                                                             │
                                                    [csv_repository.py]
                                                             │
                                                     (3. Đứt gãy: Phân biệt hoa/thường)
                                                             ▼
                                                      [avl_tree.py]
```

#### Vị trí đứt gãy 1: Web UI không gọi API khi gõ tìm kiếm
* Trong [App.tsx:L108-L115](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/ui/src/App.tsx#L108-L115), API `deckService.getDecks()` chỉ được gọi **đúng 1 lần duy nhất** khi vừa mở trang web.
* Khi bạn gõ ký tự vào ô tìm kiếm ở [MySetsView.tsx:L91-L94](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/ui/src/components/views/MySetsView.tsx#L91-L94), nó chỉ `setSearch(e.target.value)` để lọc mảng nội bộ. Backend và Cây AVL không hề được kích hoạt.

#### Vị trí đứt gãy 2: Backend Service không dùng `find_by_prefix`
* Trong commit trước đó (`9548443`), `DeckService` từng có hàm:
  ```python
  def search_decks_by_title_prefix(self, prefix: str) -> list[Deck]:
      matched = self.deck_repository.find_by_prefix("title", prefix.strip())
      return [d for d in matched if not d.is_deleted]
  ```
* Nhưng tại commit `20a9479`, hàm này đã bị thay thế hoàn toàn bởi `get_decks`:
  ```python
  # deck_service.py:L236-L240
  matched = self.deck_repository.find_by_keyword(
      keyword=clean_kw,
      search_field="title",
      is_deleted=False,
  )
  ```
* Hàm `find_by_keyword` ở [csv_repository.py:L353-L355](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/repositories/csv_repository.py#L353-L355) thực hiện phép duyệt tuyến tính **$O(N)$** và kiểm tra `clean_kw not in field_val` (tìm chuỗi con chứa ở bất kỳ đâu).
* **Kết quả:** Phương thức [find_by_prefix](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/repositories/csv_repository.py#L175-L189) và Cây AVL `prefix_search` đã bị "bỏ rơi", không có luồng nào gọi tới.

#### Vị trí đứt gãy 3: Cây AVL phân biệt chữ hoa/chữ thường (Case-sensitive)
* Tại [utils/avl_tree.py:L256-L265](file:///d:/DUTAI/module1_DUT_AI/module1_DUT_AI/utils/avl_tree.py#L256-L265):
  ```python
  node_key_str = str(node.key)
  if node_key_str < prefix and not node_key_str.startswith(prefix):
      _traverse(node.right)
  elif node_key_str.startswith(prefix):
      ...
  ```
* Khi tìm kiếm:
  * Nếu gõ chữ thường `'t'`, nó sẽ rẽ sang nhánh lớn hơn các chữ cái hoa và chỉ so khớp với `'t'`. Các từ như `"Từ vựng tiếng Anh cơ bản"` (bắt đầu bằng `'T'` hoa) sẽ bị bỏ qua.
  * Nếu gõ `'e'`, nó không tìm thấy `"English"`.

---

### Bảng tóm tắt hiện trạng

| Tầng | Thuộc tính | Cơ chế so khớp | Độ phức tạp | Đang kết nối? |
| :--- | :--- | :--- | :--- | :--- |
| **Web UI** (`MySetsView`) | `title`, `description`, `category` | Chuỗi con (`.includes()`), không phân biệt hoa/thường | $O(M)$ (duyệt mảng JS) | ❌ Không gọi API |
| **Backend API** (`main.py`) | Tham số `keyword` | Chuyển tiếp xuống Service | - | ❌ UI không gọi khi search |
| **Service** (`deck_service`) | Chỉ `title` | Chuỗi con (`in`), không phân biệt hoa/thường | $O(N)$ (quét toàn bộ deck) | ❌ Không gọi Cây AVL |
| **Repository** (`csv_repository`) | `title` | Tiền tố (`find_by_prefix`) | $O(\log N + K)$ | ❌ Không được Service gọi |
| **Cấu trúc dữ liệu** (`avl_tree`) | Khóa node | Tiền tố (`startswith`), **phân biệt hoa/thường** | $O(\log N + K)$ | ⚠️ Bị cô lập |
