import unittest
from typing import *

from src.data_structures.tree.bptree import BPTree, BPTreeNode

from test.data_structures.tree.btree_test import BTreeTestBase

T = TypeVar("T")

TEST_ORDER = 3


class BPTreeTest(BTreeTestBase):
    def create_tree(self, **kwargs: Any) -> BPTree[T]:
        return BPTree(**kwargs)

    def create_node(self, **kwargs: Any) -> BPTreeNode[T]:
        return BPTreeNode(**kwargs)


if __name__ == "__main__":
    unittest.main(BPTreeTest())