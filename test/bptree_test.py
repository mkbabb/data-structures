import unittest
from typing import *
import random

from data_structures.tree.bptree import BPTree, Node


TEST_ORDER = 3

if __name__ == "__main__":
    tree: BPTree[int] = BPTree(TEST_ORDER)

    tree.insert(1, 2, 3, 4, 5, 6, 7, 8, 9)

    tree.delete(5)
    tree.delete(7)

    s = tree.p()

    print(s)