from typing import *

T = TypeVar("T")


class Vector(Iterable[T]):
    def __init__(
        self,
        data: Optional[Union[List[T], "Vector[T]"]] = None,
        capacity: int = 10,
        fixed_size: bool = True,
    ):
        self.capacity = capacity
        self.size = 0
        self.data: List[Optional[T]] = [None] * self.capacity
        self.fixed_size = fixed_size

        if data is not None:
            for i in data:
                self.append(i)

    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return self.data[: self.size].__repr__()

    def insert(self, ix: int, value: T) -> None:
        if not self.fixed_size:
            self._grow()

        self._check_index(ix + 1)

        for i in range(self.size, ix, -1):
            self.data[i], self.data[i - 1] = self.data[i - 1], self.data[i]

        self.data[ix] = value
        self.size += 1

    def append(self, value: T) -> None:
        self.insert(len(self), value)

    def pop(self, ix: Optional[int] = None) -> T:
        ix = len(self) - 1 if ix is None else ix
        self._check_index(ix)

        for i in range(ix + 1, self.size + 1):
            self.data[i], self.data[i - 1] = self.data[i - 1], self.data[i]

        value = self.data[self.size]
        self.data[self.size] = None
        self.size -= 1

        return value

    def _check_index(self, ix: Union[int, slice]) -> None:
        if isinstance(ix, slice):
            if ix.start is not None:
                self._check_index(ix.start)
            if ix.stop is not None:
                self._check_index(ix.stop)
        else:
            if ix > self.capacity or abs(ix) - 1 > self.capacity:
                raise IndexError

    def _grow(self):
        if len(self) >= self.capacity - 1:
            self.data = self.data + [None] * self.capacity
            self.capacity = len(self.data)

    def __iter__(self) -> Generator[T, None, None]:
        for i in range(len(self)):
            value = self.data[i]
            if value is not None:
                yield value

    def __add__(self, other: Iterable[T]) -> "Vector[T]":
        for i in other:
            self.append(i)
        return self

    def __eq__(self, other: Iterable[T]) -> bool:
        return self.data[: self.size].__eq__(other)

    def __getitem__(self, ix: Union[int, slice]) -> Union[T, "Vector[T]"]:
        self._check_index(ix)

        if isinstance(ix, slice):
            stop = ix.stop if ix.stop is not None else len(self)
            ix = slice(ix.start, min(len(self), stop), ix.step)

            return Vector(data=self.data[ix], capacity=self.capacity)
        else:
            return self.data[ix]

    def __setitem__(
        self, ix: Union[int, slice], other: Union[T, Iterable[T], "Vector[T]"]
    ) -> None:
        self._check_index(ix)

        if isinstance(other, Vector):
            other = other.data[ix]

        self.data.__setitem__(ix, other)


if __name__ == "__main__":
    v = Vector([1, 2, 3, 4], fixed_size=False, capacity=5)
    v.append(5)
    v.append(6)