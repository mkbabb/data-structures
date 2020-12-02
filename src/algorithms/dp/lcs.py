from typing import *
from dataclasses import dataclass


def factorial(n: int) -> int:
    p = 1
    while n > 0:
        p *= n
        n -= 1
    return p


get_bit: Callable[[int, int], int] = lambda n, pos: (n & (1 << pos)) >> pos


def iter_combinations(m: int) -> Iterable[List[bool]]:
    c = factorial(m)

    for n in range(1, c + 1):
        yield [get_bit(n, i) == 1 for i in range(m)]


def lcs_k(*words: str) -> str:
    words = list(words)
    dp: Dict[str, str] = {}

    def recurse(ixs: List[int]) -> str:
        if any(i < 0 for i in ixs):
            return ""

        key = "".join(map(str, ixs))

        if key in dp:
            return dp[key]

        word = ""
        c = words[0][ixs[0]]

        if all(c == word[i] for i, word in zip(ixs, words)):
            ixs = [i - 1 for i in ixs]
            word = recurse(ixs) + c

        t_words = []

        for combin in iter_combinations(len(words)):
            t_words.append(recurse([i - 1 if j else i for i, j in zip(ixs, combin)]))

        dp[key] = max(
            word,
            *t_words,
            key=len,
        )

        return dp[key]

    ixs = [len(i) - 1 for i in words]
    return recurse(ixs)


def lcs(s1: str, s2: str) -> str:
    dp: Dict[str, str] = {}

    def recurse(i: int, j: int) -> str:
        if i >= len(s1) or j >= len(s2):
            return ""

        key = f"{i},{j}"

        if key in dp:
            return dp[key]

        word = s1[i] + recurse(i + 1, j + 1) if s1[i] == s2[j] else ""

        dp[key] = max(
            word,
            recurse(i, j + 1),
            recurse(i + 1, j),
            key=len,
        )

        return dp[key]

    return recurse(0, 0)


if __name__ == "__main__":
    s1 = "fatajatbas"
    s2 = "kilajatbastheokthatsnotveryajat"

    s = lcs(s1, s2)
    print(s)
