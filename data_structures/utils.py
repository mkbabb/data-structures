from typing import *

T = TypeVar("T")
Comparator = Callable[[T, T], int]

default_comparator = lambda x, y: -1 if x < y else 1 if x > y else 0


def bisect_left(arr: List[T], x: T, comparator: Comparator = default_comparator) -> int:
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
                return midpoint
        else:
            return -1 * (low + 1)

    return recurse(0, len(arr) - 1)