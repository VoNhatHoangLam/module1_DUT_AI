"""Cấu trúc Dữ liệu Cây tìm kiếm nhị phân tự cân bằng (AVL Tree).

Đảm bảo độ phức tạp thời gian cho các thao tác tìm kiếm, chèn, xóa và
cập nhật luôn đạt O(log N) trong trường hợp xấu nhất (worst-case).
"""

from __future__ import annotations

from typing import Any, Callable, Generic, Iterator, Optional, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class _AVLNode(Generic[K, V]):
    """Nút nội bộ trong cây AVL."""

    __slots__ = ("key", "value", "left", "right", "height")

    def __init__(self, key: K, value: V) -> None:
        self.key: K = key
        self.value: V = value
        self.left: Optional[_AVLNode[K, V]] = None
        self.right: Optional[_AVLNode[K, V]] = None
        self.height: int = 1


def _node_height(node: Optional[_AVLNode[Any, Any]]) -> int:
    return node.height if node is not None else 0


def _node_balance(node: Optional[_AVLNode[Any, Any]]) -> int:
    return _node_height(node.left) - _node_height(node.right) if node is not None else 0


def _update_node_height(node: _AVLNode[Any, Any]) -> None:
    node.height = 1 + max(_node_height(node.left), _node_height(node.right))


class AVLTree(Generic[K, V]):
    """Cây tìm kiếm nhị phân tự cân bằng AVL cho khóa đơn nhất.

    Mọi thao tác tìm kiếm, chèn, cập nhật, xóa đều có độ phức tạp O(log N).
    """

    __slots__ = ("_root", "_size")

    def __init__(self) -> None:
        self._root: Optional[_AVLNode[K, V]] = None
        self._size: int = 0

    @property
    def root(self) -> Optional[_AVLNode[K, V]]:
        """Trả về nút gốc của cây."""
        return self._root

    def is_empty(self) -> bool:
        """Kiểm tra cây có rỗng hay không."""
        return self._size == 0

    def height(self) -> int:
        """Chiều cao của cây (O(1))."""
        return _node_height(self._root)

    def search(self, key: K) -> Optional[V]:
        """Tìm kiếm giá trị theo khóa với độ phức tạp O(log N).

        Trả về giá trị nếu tìm thấy, ngược lại trả về None.
        """
        curr = self._root
        while curr is not None:
            if key == curr.key:
                return curr.value
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return None

    def contains(self, key: K) -> bool:
        """Kiểm tra sự tồn tại của khóa với độ phức tạp O(log N)."""
        return self.search(key) is not None

    def __contains__(self, key: K) -> bool:
        return self.contains(key)

    def min_key(self) -> Optional[K]:
        """Tìm khóa nhỏ nhất trong cây với độ phức tạp O(log N)."""
        if self._root is None:
            return None
        curr = self._root
        while curr.left is not None:
            curr = curr.left
        return curr.key

    def max_key(self) -> Optional[K]:
        """Tìm khóa lớn nhất trong cây với độ phức tạp O(log N)."""
        if self._root is None:
            return None
        curr = self._root
        while curr.right is not None:
            curr = curr.right
        return curr.key

    def insert(self, key: K, value: V, replace: bool = False) -> None:
        """Chèn một cặp (khóa, giá trị) vào cây với độ phức tạp O(log N).

        Args:
            key: Khóa cần chèn.
            value: Giá trị tương ứng.
            replace: Nếu True và khóa đã tồn tại, thay thế giá trị cũ.
                     Nếu False và khóa đã tồn tại, ném ngoại lệ KeyError.
        """
        inserted = [False]

        def _insert_rec(node: Optional[_AVLNode[K, V]]) -> _AVLNode[K, V]:
            if node is None:
                inserted[0] = True
                return _AVLNode(key, value)

            if key == node.key:
                if replace:
                    node.value = value
                    return node
                raise KeyError(f"Khóa {key!r} đã tồn tại trong cây AVL")

            if key < node.key:
                node.left = _insert_rec(node.left)
            else:
                node.right = _insert_rec(node.right)

            _update_node_height(node)
            return self._rebalance(node)

        self._root = _insert_rec(self._root)
        if inserted[0]:
            self._size += 1

    def update(self, key: K, value: V) -> bool:
        """Cập nhật giá trị cho khóa đã có với độ phức tạp O(log N).

        Trả về True nếu cập nhật thành công, False nếu khóa không tồn tại.
        """
        curr = self._root
        while curr is not None:
            if key == curr.key:
                curr.value = value
                return True
            elif key < curr.key:
                curr = curr.left
            else:
                curr = curr.right
        return False

    def delete(self, key: K) -> bool:
        """Xóa một khóa khỏi cây với độ phức tạp O(log N).

        Trả về True nếu xóa thành công, False nếu khóa không tồn tại.
        """
        deleted = [False]

        def _delete_rec(node: Optional[_AVLNode[K, V]]) -> Optional[_AVLNode[K, V]]:
            if node is None:
                return None

            if key < node.key:
                node.left = _delete_rec(node.left)
            elif key > node.key:
                node.right = _delete_rec(node.right)
            else:
                deleted[0] = True
                # Trường hợp có 0 hoặc 1 nút con
                if node.left is None:
                    return node.right
                elif node.right is None:
                    return node.left

                # Trường hợp có cả 2 nút con: tìm nút kế vị nhỏ nhất bên cây con phải
                successor = node.right
                while successor.left is not None:
                    successor = successor.left

                node.key = successor.key
                node.value = successor.value
                node.right = _delete_min(node.right)

            _update_node_height(node)
            return self._rebalance(node)

        def _delete_min(node: _AVLNode[K, V]) -> Optional[_AVLNode[K, V]]:
            if node.left is None:
                return node.right
            node.left = _delete_min(node.left)
            _update_node_height(node)
            return self._rebalance(node)

        self._root = _delete_rec(self._root)
        if deleted[0]:
            self._size -= 1
        return deleted[0]

    def clear(self) -> None:
        """Xóa toàn bộ cây."""
        self._root = None
        self._size = 0

    def inorder(self) -> list[V]:
        """Duyệt trung thứ tự (In-order Traversal) trả về danh sách giá trị theo thứ tự khóa tăng dần.

        Độ phức tạp O(N) trong bộ nhớ RAM, không đụng tới đĩa.
        """
        result: list[V] = []
        stack: list[_AVLNode[K, V]] = []
        curr = self._root
        while curr is not None or stack:
            while curr is not None:
                stack.append(curr)
                curr = curr.left
            curr = stack.pop()
            result.append(curr.value)
            curr = curr.right
        return result

    def inorder_items(self) -> list[tuple[K, V]]:
        """Duyệt trung thứ tự trả về danh sách các cặp (khóa, giá trị)."""
        result: list[tuple[K, V]] = []
        stack: list[_AVLNode[K, V]] = []
        curr = self._root
        while curr is not None or stack:
            while curr is not None:
                stack.append(curr)
                curr = curr.left
            curr = stack.pop()
            result.append((curr.key, curr.value))
            curr = curr.right
        return result

    def is_balanced(self) -> bool:
        """Kiểm tra điều kiện cân bằng của cây AVL (dành cho kiểm thử)."""
        def _check(node: Optional[_AVLNode[K, V]]) -> bool:
            if node is None:
                return True
            if abs(_node_balance(node)) > 1:
                return False
            return _check(node.left) and _check(node.right)
        return _check(self._root)

    def __len__(self) -> int:
        return self._size

    def __iter__(self) -> Iterator[V]:
        return iter(self.inorder())

    # --- Các phép quay tái cân bằng cây AVL ---

    def _rotate_right(self, y: _AVLNode[K, V]) -> _AVLNode[K, V]:
        r"""Phép quay phải đơn (Right Rotation).

             y                               x
            / \     Right Rotation          /  \
           x   T3   -------------->        T1   y
          / \                                  / \
         T1  T2                               T2  T3
        """
        x = y.left
        assert x is not None
        t2 = x.right

        x.right = y
        y.left = t2

        _update_node_height(y)
        _update_node_height(x)
        return x

    def _rotate_left(self, x: _AVLNode[K, V]) -> _AVLNode[K, V]:
        r"""Phép quay trái đơn (Left Rotation).

           x                                y
          / \      Left Rotation           /  \
         T1  y    --------------->        x   T3
            / \                          / \
           T2  T3                       T1  T2
        """
        y = x.right
        assert y is not None
        t2 = y.left

        y.left = x
        x.right = t2

        _update_node_height(x)
        _update_node_height(y)
        return y

    def _rebalance(self, node: _AVLNode[K, V]) -> _AVLNode[K, V]:
        """Thực hiện cân bằng lại nút nếu chênh lệch chiều cao > 1."""
        balance = _node_balance(node)

        # Lệch trái (Left Heavy)
        if balance > 1:
            assert node.left is not None
            # Trường hợp Trái - Phải (Left-Right)
            if _node_balance(node.left) < 0:
                node.left = self._rotate_left(node.left)
            # Trường hợp Trái - Trái (Left-Left)
            return self._rotate_right(node)

        # Lệch phải (Right Heavy)
        if balance < -1:
            assert node.right is not None
            # Trường hợp Phải - Trái (Right-Left)
            if _node_balance(node.right) > 0:
                node.right = self._rotate_right(node.right)
            # Trường hợp Phải - Phải (Right-Right)
            return self._rotate_left(node)

        return node


class MultiAVLTree(Generic[K, V]):
    """Cây AVL hỗ trợ một khóa trỏ tới nhiều giá trị (Secondary Index).

    Được cài đặt dựa trên AVLTree[K, list[V]], đảm bảo:
    - Tìm kiếm node theo khóa: O(log N).
    - Thêm / Xóa phần tử theo khóa: O(log N).
    """

    __slots__ = ("_tree", "_total_items")

    def __init__(self) -> None:
        self._tree: AVLTree[K, list[V]] = AVLTree()
        self._total_items: int = 0

    def search(self, key: K) -> list[V]:
        """Tìm kiếm danh sách các bản ghi có khóa tương ứng với O(log N).

        Trả về bản sao danh sách kết quả (hoặc rỗng nếu không có).
        """
        items = self._tree.search(key)
        return list(items) if items is not None else []

    def contains(self, key: K) -> bool:
        """Kiểm tra sự tồn tại của khóa với O(log N)."""
        return self._tree.contains(key)

    def insert(self, key: K, value: V) -> None:
        """Chèn một phần tử vào khóa tương ứng với O(log N)."""
        items = self._tree.search(key)
        if items is not None:
            items.append(value)
        else:
            self._tree.insert(key, [value], replace=False)
        self._total_items += 1

    def remove(
        self,
        key: K,
        value: V,
        identifier_func: Optional[Callable[[V], Any]] = None,
    ) -> bool:
        """Xóa một bản ghi cụ thể khỏi khóa với O(log N).

        Args:
            key: Khóa của chỉ mục.
            value: Đối tượng bản ghi cần xóa.
            identifier_func: Hàm trích xuất định danh (ví dụ lambda r: r.card_id)
                             để so sánh chính xác nếu không muốn dùng toán tử ==.
        """
        items = self._tree.search(key)
        if items is None:
            return False

        found_idx = -1
        if identifier_func is not None:
            target_id = identifier_func(value)
            for idx, item in enumerate(items):
                if identifier_func(item) == target_id:
                    found_idx = idx
                    break
        else:
            try:
                found_idx = items.index(value)
            except ValueError:
                pass

        if found_idx != -1:
            items.pop(found_idx)
            self._total_items -= 1
            if not items:
                self._tree.delete(key)
            return True
        return False

    def remove_by_id(
        self,
        identifier: Any,
        identifier_func: Callable[[V], Any],
    ) -> bool:
        """Xóa bản ghi khỏi chỉ mục dựa vào định danh ở bất kỳ khóa nào."""
        for key, bucket in self._tree.inorder_items():
            for idx, item in enumerate(bucket):
                if identifier_func(item) == identifier:
                    bucket.pop(idx)
                    self._total_items -= 1
                    if not bucket:
                        self._tree.delete(key)
                    return True
        return False

    def update_record(
        self,
        old_key: K,
        new_key: K,
        value: V,
        identifier_func: Optional[Callable[[V], Any]] = None,
    ) -> None:
        """Cập nhật bản ghi khi giá trị khóa của chỉ mục có thể đã thay đổi."""
        if identifier_func is not None:
            # Gỡ bỏ bản ghi cũ khỏi bucket cũ hoặc tìm theo định danh nếu đã bị thay đổi
            removed = self.remove(old_key, value, identifier_func=identifier_func)
            if not removed:
                self.remove_by_id(identifier_func(value), identifier_func)
            self.insert(new_key, value)
        else:
            self.remove(old_key, value)
            self.insert(new_key, value)

    def inorder(self) -> list[V]:
        """Duyệt toàn bộ các bản ghi theo thứ tự khóa tăng dần."""
        result: list[V] = []
        for bucket in self._tree.inorder():
            result.extend(bucket)
        return result

    def clear(self) -> None:
        """Xóa toàn bộ chỉ mục."""
        self._tree.clear()
        self._total_items = 0

    def __len__(self) -> int:
        return self._total_items
