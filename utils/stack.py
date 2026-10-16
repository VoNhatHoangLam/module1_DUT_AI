"""Cài đặt ngăn xếp LIFO dùng cho phiên làm bài quiz."""

from __future__ import annotations

from typing import Generic, Iterable, Optional, TypeVar


T = TypeVar("T")


class EmptyStackError(IndexError):
    """Ngăn xếp rỗng nên không thể lấy phần tử."""


class Stack(Generic[T]):
    """Ngăn xếp LIFO tự cài đặt bằng danh sách liên kết đơn."""

    __slots__ = ("_top", "_size")

    class _Node(Generic[T]):
        __slots__ = ("value", "next")

        def __init__(self, value: T, next_node: Optional["Stack._Node[T]"] = None) -> None:
            self.value = value
            self.next = next_node

    def __init__(self, values: Optional[Iterable[T]] = None) -> None:
        self._top: Optional[Stack._Node[T]] = None
        self._size = 0
        if values is not None:
            for value in values:
                self.push(value)

    def push(self, value: T) -> None:
        self._top = self._Node(value, self._top)
        self._size += 1

    def pop(self) -> T:
        if self._top is None:
            raise EmptyStackError("Không thể lấy phần tử từ ngăn xếp rỗng")
        node = self._top
        self._top = node.next
        node.next = None
        self._size -= 1
        return node.value

    def peek(self) -> T:
        if self._top is None:
            raise EmptyStackError("Không thể xem phần tử của ngăn xếp rỗng")
        return self._top.value

    def is_empty(self) -> bool:
        return self._size == 0

    def clear(self) -> None:
        self._top = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def __bool__(self) -> bool:
        return not self.is_empty()
