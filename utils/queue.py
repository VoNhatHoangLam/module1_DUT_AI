"""Cài đặt hàng đợi FIFO bằng danh sách liên kết đơn."""

from __future__ import annotations

from typing import Generic, Iterable, Optional, TypeVar


T = TypeVar("T")


class EmptyQueueError(IndexError):
    """Hàng đợi đang rỗng nên không thể lấy phần tử."""


class _QueueNode(Generic[T]):
    """Một nút nội bộ của hàng đợi."""

    __slots__ = ("value", "next")

    def __init__(self, value: T) -> None:
        self.value = value
        self.next: Optional[_QueueNode[T]] = None


class Queue(Generic[T]):
    """Hàng đợi FIFO tự cài đặt, thêm và lấy phần tử với O(1)."""

    __slots__ = ("_front", "_rear", "_size")

    def __init__(self, values: Optional[Iterable[T]] = None) -> None:
        self._front: Optional[_QueueNode[T]] = None
        self._rear: Optional[_QueueNode[T]] = None
        self._size = 0

        if values is not None:
            for value in values:
                self.enqueue(value)

    def enqueue(self, value: T) -> None:
        """Thêm một phần tử vào cuối hàng đợi."""

        node = _QueueNode(value)
        if self._rear is None:
            self._front = node
            self._rear = node
        else:
            self._rear.next = node
            self._rear = node
        self._size += 1

    def dequeue(self) -> T:
        """Lấy và loại phần tử đầu hàng đợi."""

        if self._front is None:
            raise EmptyQueueError("Không thể lấy phần tử từ hàng đợi rỗng")

        node = self._front
        self._front = node.next
        node.next = None
        self._size -= 1

        if self._front is None:
            self._rear = None

        return node.value

    def peek(self) -> T:
        """Xem phần tử đầu hàng đợi mà không loại bỏ nó."""

        if self._front is None:
            raise EmptyQueueError("Không thể xem phần tử của hàng đợi rỗng")
        return self._front.value

    def is_empty(self) -> bool:
        """Trả về True khi hàng đợi không còn phần tử."""

        return self._size == 0

    def clear(self) -> None:
        """Loại toàn bộ phần tử khỏi hàng đợi."""

        self._front = None
        self._rear = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return not self.is_empty()
