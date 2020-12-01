import unittest
from typing import *
import random

from src.data_structures.tree.btree import BTree, BTreeNode
from src.data_structures.utils.utils import default_comparator


T = TypeVar("T")

TEST_ORDER = 4

random.seed(1)


class TreeTest(unittest.TestCase):
    def assertSorted(self, iterable: Iterable, comparator=default_comparator) -> None:
        one = iter(iterable)
        two = iter(iterable)

        next(two)

        for i, j in zip(one, two):
            self.assertTrue(comparator(i, j) < 0)


class BTreeTestBase(TreeTest):
    def create_tree(self, **kwargs: Any) -> BTree[T]:
        return BTree(**kwargs)

    def create_node(self, **kwargs: Any) -> BTreeNode[T]:
        return BTreeNode(**kwargs)

    def assertTreeSorted(self, tree: BTree):
        values = []
        tree.for_each(lambda x: values.append(x))

        self.assertSorted(values, tree.comparator)

    def test_unsorted_1(self):
        tree = self.create_tree(order=TEST_ORDER)
        tree.insert(list("qwertyuiopasdfghjklzxcvbnm"))
        self.assertTreeSorted(tree)

    def test_unsorted_2(self):
        tree = self.create_tree(order=TEST_ORDER)
        n = 1000

        nums = list(range(n))
        random.shuffle(nums)

        tree.insert(*nums)

        self.assertTreeSorted(tree)

    def test_delete_transfer(self):
        pass

    def test_insert_delete_many(self):
        n = 1000
        nums = list(range(n))
        random.shuffle(nums)

        for order in range(3, 12):
            print(f"order: {order}")
            tree = self.create_tree(order=order)

            for num in nums:
                tree.insert(num)

            random.shuffle(nums)

            for i, num in enumerate(nums):
                self.assertTreeSorted(tree)
                tree.delete(num)


class BTreeTest(BTreeTestBase):
    def setup_rotate(self) -> List[BTreeNode]:
        parent = self.create_node(tree_order=TEST_ORDER)
        parent.values = [10]

        child_values = [0, 11]

        children = [
            self.create_node(
                tree_order=TEST_ORDER,
                children=[BTreeNode(tree_order=TEST_ORDER, values=[i])],
                values=[i],
                parent=parent,
            )
            for i in child_values
        ]
        parent.children = children

        return children

    def test_right_rotate(self) -> None:
        children = self.setup_rotate()

        children[0].rotate(0, children[1], False)

        self.assertEqual(children[0].values, [0, 10])

        self.assertEqual(children[0].children[0].values, [0])
        self.assertEqual(children[0].children[1].values, [11])

    def test_left_rotate(self) -> None:
        children = self.setup_rotate()

        children[1].rotate(0, children[0], True)

        self.assertEqual(children[1].values, [10, 11])

        self.assertEqual(children[1].children[0].values, [0])
        self.assertEqual(children[1].children[1].values, [11])

    def test_insert_new_root(self):
        tree = self.create_tree(order=TEST_ORDER)

        tree.insert(1, 2, 3, 4)

        self.assertEqual(tree.root.values[0], 3)

        self.assertEqual(tree.root.children[0].values, [1, 2])
        self.assertEqual(tree.root.children[1].values, [4])

        self.assertTreeSorted(tree)

    def test_delete_merge_1(self):
        tree = self.create_tree(order=TEST_ORDER)

        tree.insert(1, 2, 3, 4)
        tree.delete(1)
        tree.delete(2)

        self.assertEqual(tree.root.values, [3, 4])

        self.assertTreeSorted(tree)

    def test_delete_merge_2(self):
        tree = self.create_tree(order=TEST_ORDER)

        tree.insert(*range(1, 14))
        tree.delete(8)
        tree.delete(7)
        tree.delete(6)
        tree.delete(5)
        tree.delete(4)
        tree.delete(2)

        self.assertEqual(tree.root.values, [9, 12])

        self.assertEqual(tree.root.children[0].values, [1, 3])
        self.assertEqual(tree.root.children[1].values, [10, 11])
        self.assertEqual(tree.root.children[2].values, [13])

        self.assertTreeSorted(tree)

    def test_merge_left(self):
        tree = self.create_tree(order=7)

        tree.insert(1, 2, 3, 4, 5, 6, 7)

        tree.delete(3)

        self.assertEqual(tree.root.values, [1, 2, 4, 5, 6, 7])

    def test_merge_right(self):
        tree = self.create_tree(order=7)

        tree.insert(1, 2, 3, 4, 5, 6, 7)

        tree.delete(5)

        self.assertEqual(tree.root.values, [1, 2, 3, 4, 6, 7])

    def test_merge_transfer_left(self):
        tree = self.create_tree(order=7)

        tree.insert(1, 2, 3, 4, 5, 6, 7, 8)
        tree.insert(0)

        tree.delete(3)
        tree.delete(2)

        self.assertEqual(tree.root.values, [5])
        self.assertEqual(tree.root.children[0].values, [0, 1, 4])
        self.assertEqual(tree.root.children[1].values, [6, 7, 8])

    def test_merge_transfer_right(self):
        tree = self.create_tree(order=7)

        tree.insert(1, 2, 3, 4, 5, 6, 7, 8)
        tree.insert(0)

        tree.delete(5)
        tree.delete(6)

        self.assertEqual(tree.root.values, [3])
        self.assertEqual(tree.root.children[0].values, [0, 1, 2])
        self.assertEqual(tree.root.children[1].values, [4, 7, 8])


if __name__ == "__main__":
    unittest.main(BTreeTest())