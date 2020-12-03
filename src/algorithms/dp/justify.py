from typing import *
import math


def badness(words: List[str], page_width: int) -> float:
    total_len = sum(len(i) for i in words) + len(words) - 1
    if total_len > page_width:
        return float("inf")
    else:
        return math.pow(page_width - total_len, 3)


def justify(words: List[str], page_width: int):
    N = len(words)
    dp: Dict[int, float] = {}
    breaks = [0] * N

    p_badness: Callable[[List[str]], float] = lambda x: badness(x, page_width)

    def recurse(i: int) -> float:
        if i >= N:
            return 0
        elif i in dp:
            return dp[i]
        else:
            splits = []

            for j in range(i + 1, N + 1):
                sub_words = words[i:j]

                split_cost = recurse(j) + p_badness(sub_words)

                splits.append((sub_words, split_cost))

            min_sub_words = min(splits, key=lambda x: x[1])
            breaks[i] = i + splits.index(min_sub_words) + 1
            dp[i] = min_sub_words[1]

            return dp[i]

    recurse(0)

    lines = []
    linebreaks = []

    i = 0
    while True:

        linebreaks.append(breaks[i])
        i = breaks[i]

        if i == len(words):
            linebreaks.append(0)
            break

    for i in range(len(linebreaks)):
        lines.append(" ".join(words[linebreaks[i - 1] : linebreaks[i]]).strip())

    for line in lines:
        print(line)


words = """Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy
eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam
voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet
clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit
amet. Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam
nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed
diam voluptua. At vero eos et accusam et justo duo dolores et ea rebum. Stet
clita kasd gubergren, no sea takimata sanctus est Lorem ipsum dolor sit amet.""".replace(
    "\n", " "
).split(
    " "
)

justify(words, 80)
