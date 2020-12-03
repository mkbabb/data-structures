from typing import *


T = TypeVar("T")
Comparator = Callable[[T, T], int]

default_comparator = lambda x, y: -1 if x < y else 1 if x > y else 0


def bisect(
    arr: List[T],
    x: T,
    comparator: Comparator = default_comparator,
    left: bool = True,
    negate_found: bool = True,
    start: Optional[int] = None,
    stop: Optional[int] = None,
) -> int:
    def recurse(low: int, high: int) -> int:
        midpoint = (high + low) // 2

        if low <= high:
            midvalue = arr[midpoint]

            comp = comparator(x, midvalue)

            if comp < 0:
                return recurse(low, midpoint - 1)
            elif comp > 0:
                return recurse(midpoint + 1, high)
            else:
                return midpoint if left else midpoint + 1
        else:
            return -1 * (low + 1) if negate_found else low

    start = 0 if start is None else start
    stop = len(arr) - 1 if stop is None else stop

    return recurse(start, stop)


def bisect_left(
    arr: List[T],
    x: T,
    comparator: Comparator = default_comparator,
    negate_found: bool = True,
    start: Optional[int] = None,
    stop: Optional[int] = None,
) -> int:
    return bisect(arr, x, comparator, True, negate_found, start, stop)


def bisect_right(
    arr: List[T],
    x: T,
    comparator: Comparator = default_comparator,
    negate_found: bool = True,
    start: Optional[int] = None,
    stop: Optional[int] = None,
) -> int:
    return bisect(arr, x, comparator, False, negate_found, start, stop)


if __name__ == "__main__":
    arr = [1, 2, 4]

    x = 3

    ix = bisect_right(arr, x)
    ix = -1 * (ix + 1)

    print("h")
