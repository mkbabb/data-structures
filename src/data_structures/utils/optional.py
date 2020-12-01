from typing import *

T = TypeVar("T")
S = TypeVar("S")


class optional(Generic[T]):
    def __init__(self, value: Optional[T]):
        self.value = value

    def __bool__(self) -> bool:
        return self.value is not None

    def map(self, func: Callable[[T], T]) -> "optional[T]":
        if self:
            return self.__class__(func(self.value))
        else:
            return self

    def __or__(self, other: Union[S, Callable[[T], S]]) -> "optional[T]":
        return optional(self.value_or(other))

    def value_or(self, other: Union[S, Callable[[T], S]]) -> Union[T, S]:
        if self:
            return self.value
        else:
            if callable(other):
                return other()
            else:
                return other


x = optional(None)

t = (x | 99).value_or(99)
