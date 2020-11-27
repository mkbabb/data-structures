import unittest
from typing import *
import random

from data_structures import BTree, Node, Comparator, T, default_comparator


TEST_ORDER = 4


class BTreeTest(unittest.TestCase):
    def setup_rotate(self) -> List[Node]:
        parent = Node(tree_order=TEST_ORDER)
        parent.values = [10]

        child_values = [0, 11]

        children = [
            Node(
                tree_order=TEST_ORDER,
                children=[Node(tree_order=TEST_ORDER, values=[i])],
                values=[i],
                parent=parent,
            )
            for i in child_values
        ]
        parent.children = children

        return children

    def test_right_rotate(self) -> None:
        children = self.setup_rotate()
        BTree._rotate(0, children[0], children[1], False)

        self.assertEqual(children[0].values, [0, 10])

        self.assertEqual(children[0].children[0].values, [0])
        self.assertEqual(children[0].children[1].values, [11])

    def test_left_rotate(self) -> None:
        children = self.setup_rotate()

        BTree._rotate(0, children[1], children[0], True)

        self.assertEqual(children[1].values, [10, 11])

        self.assertEqual(children[1].children[0].values, [0])
        self.assertEqual(children[1].children[1].values, [11])

    def assertSorted(self, iterable: Iterable, comparator=default_comparator):
        one = iter(iterable)
        two = iter(iterable)

        next(two)

        for i, j in zip(one, two):
            self.assertTrue(comparator(i, j) < 0)

    def assertTreeSorted(self, tree: BTree):
        values = []
        tree.for_each(lambda x: values.append(x))

        self.assertSorted(values, tree.comparator)

    def test_insert_new_root(self):
        tree = BTree(order=TEST_ORDER)

        tree.insert(1, 2, 3, 4)

        self.assertEqual(tree.root.values[0], 3)

        self.assertEqual(tree.root.children[0].values, [1, 2])
        self.assertEqual(tree.root.children[1].values, [4])

        self.assertTreeSorted(tree)

    def test_insert_many(self):
        for order in range(TEST_ORDER, 12):
            tree = BTree(order=order)
            tree.insert(*range(1000, 0, -1))
            self.assertTreeSorted(tree)

    def test_unsorted_1(self):
        tree = BTree(order=TEST_ORDER)
        tree.insert(list("qwertyuiopasdfghjklzxcvbnm"))
        self.assertTreeSorted(tree)

    def test_unsorted_2(self):
        tree = BTree(order=TEST_ORDER)
        n = 1000
        nums = set(random.randint(0, n) for _ in range(n))

        tree.insert(*nums)

        self.assertTreeSorted(tree)

    def test_delete_merge_1(self):
        tree = BTree(order=TEST_ORDER)

        tree.insert(1, 2, 3, 4)
        tree.delete(1)
        tree.delete(2)

        self.assertEqual(tree.root.values, [3, 4])

        self.assertTreeSorted(tree)

    def test_delete_merge_2(self):
        tree = BTree(order=TEST_ORDER)

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

    def test_delete_transfer(self):
        pass


if __name__ == "__main__":
    unittest.main()