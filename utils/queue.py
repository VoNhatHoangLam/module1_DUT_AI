"""Cài đặt hàng đợi FIFO bằng danh sách liên kết đơn với độ phức tạp O(1)."""

from __future__ import annotations

from typing import Generic, Iterable, Iterator, Optional, TypeVar


T = TypeVar("T")


class EmptyQueueError(IndexError):
    """Hàng đợi đang rỗng nên không thể lấy phần tử."""


class _QueueNode(Generic[T]):
    """Một nút nội bộ của hàng đợi liên kết đơn."""

    __slots__ = ("value", "next")

    def __init__(self, value: T) -> None:
        self.value = value
        self.next: Optional[_QueueNode[T]] = None


class Queue(Generic[T]):
    """Hàng đợi FIFO tự cài đặt bằng danh sách liên kết đơn, thêm và lấy với O(1)."""

    __slots__ = ("_front", "_rear", "_size")

    def __init__(self, values: Optional[Iterable[T]] = None) -> None:
        self._front: Optional[_QueueNode[T]] = None
        self._rear: Optional[_QueueNode[T]] = None
        self._size = 0

        if values is not None:
            for value in values:
                self.enqueue(value)

    def enqueue(self, value: T) -> None:
        """Thêm một phần tử vào cuối hàng đợi (rear) với O(1)."""
        node = _QueueNode(value)
        if self._rear is None:
            self._front = node
            self._rear = node
        else:
            self._rear.next = node
            self._rear = node
        self._size += 1

    def dequeue(self) -> T:
        """Lấy và loại phần tử ở đầu hàng đợi (front) với O(1)."""
        if self._front is None:
            raise EmptyQueueError("Không thể lấy phần tử từ hàng đợi rỗng")

        node = self._front
        self._front = self._front.next
        if self._front is None:
            self._rear = None

        node.next = None
        self._size -= 1
        return node.value

    def peek(self) -> T:
        """Xem phần tử ở đầu hàng đợi (front) mà không loại bỏ nó với O(1)."""
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

    def __iter__(self) -> Iterator[T]:
        curr = self._front
        while curr is not None:
            yield curr.value
            curr = curr.next
