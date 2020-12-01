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
    # unittest.main(BPTreeTest())
    tree = BPTree(4)
    tree.insert(*range(1, 20))
    tree.for_each(print)

    tree.delete(10)
    tree.delete(11)
    tree.delete(12)
    tree.delete(13)
    tree.delete(14)
    
    tree.for_each(print)