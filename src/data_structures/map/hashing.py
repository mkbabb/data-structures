import math
from typing import *

PHI = (1 + math.sqrt(5)) / 2


def polynomial_hash(s: str, r: int) -> int:
    sum = 0

    for i in range(len(s)):
        print(ord(s[i]))
        sum += (r ** i) * ord(s[i])

    return sum


def additive_hash(s: str) -> int:
    return polynomial_hash(s, 1)


def get_fractional(x: float) -> float:
    return x - math.floor(x)


def mad_compress(hash: int, alpha: int, beta: int, m: int) -> int:
    return (alpha * hash + beta) % m


def division_compress(hash: int, m: int) -> int:
    return mad_compress(hash, 1, 0, m)


def phi_compress(hash: int, m: int) -> int:
    frac = get_fractional(hash / PHI)
    return math.floor(m * frac)
