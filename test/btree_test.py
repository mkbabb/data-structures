import unittest
from typing import *

from data_structures import BTree, Node


class BTreeTest(unittest.TestCase):
    def setup_rotate(self) -> List[Node]:
        parent = Node()
        parent.values = [10]

        child_values = [0, 11]

        children = [Node([Node(values=[i])], [i], parent) for i in child_values]
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


if __name__ == "__main__":
    unittest.main()