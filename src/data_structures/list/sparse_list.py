from typing import *

T = TypeVar("T")


def popcount(i: int, max_count: int = 64) -> int:
    count = 0
    while i != 0 and count < max_count:
        count += 1 if i & 1 == 1 else 0
        i >>= 1
    return count


def set_nth_bit(i: int, n: int, b: int) -> int:
    return (i & (~(1 << n))) | (b << n)


class SparseList(Generic[T]):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data: List[T] = []
        self.data_map: List[Optional[int]] = [None] * capacity
        self.size = 0

    def __repr__(self) -> str:
        return self.data.__repr__()

    def to_sparse_index(self, ix: int) -> Optional[int]:
        return self.data_map[ix]

    def insert(self, ix: int, value: T) -> None:
        if ix > self.capacity:
            raise IndexError

        self.data.append(value)
        self.data_map[ix] = self.size
        self.size += 1

    def copy(self) -> "SparseList[T]":
        out = self.__class__(self.capacity)
        out.data = list(self.data)
        out.data_map = list(self.data_map)
        out.size = self.size
        return out

    def __list__(self) -> "SparseList[T]":
        return self.copy()

    def __getitem__(self, ix: int) -> Optional[T]:
        if (six := self.to_sparse_index(ix)) is not None:
            return self.data[six]
        else:
            return None

    def __setitem__(self, ix: int, value: T) -> None:
        if (six := self.to_sparse_index(ix)) is None:
            self.insert(ix, value)
        else:
            self.data[six] = value

    def __iter__(self) -> Generator[T, None, None]:
        for i in self.data:
            yield i


if __name__ == "__main__":
    a = SparseList[str](5)
    a.insert(0, "a")
    a.insert(3, "b")
    a.insert(1, "c")
    a.insert(4, "d")

    ix = a.to_sparse_index(3)