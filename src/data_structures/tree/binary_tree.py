from typing import *

from src.data_structures.tree import Tree, TreeNode
from src.data_structures.utils.utils import Comparator, bisect, default_comparator

T = TypeVar("T")


class BinaryNode(TreeNode[T]):
    def __init__(
        self,
        value: Optional[T] = None,
        left: Optional["BinaryNode[T]"] = None,
        right: Optional["BinaryNode[T]"] = None,
        parent: Optional["BinaryNode[T]"] = None,
    ) -> None:
        super().__init__(tree_order=1, children=[left, right], parent=parent)
        if value is not None:
            self.values.append(value)

    def rotate(self, go_left: bool):
        left_node, right_node = self.left, self.right

        if go_left:
            right_node.parent = self.parent

            self.parent = right_node
            self.right = right_node.left
            right_node.left = self

            return right_node
        else:
            left_node.parent = self.parent

            self.parent = left_node
            self.left = left_node.right
            left_node.right = self

            return left_node

    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    @property
    def left(self) -> T:
        return self.children[0]

    @left.setter
    def left(self, other: T) -> None:
        self.children[0] = other

    @property
    def right(self) -> T:
        return self.children[1]

    @right.setter
    def right(self, other: T) -> None:
        self.children[1] = other

    def value(self) -> T:
        return self.values[0]


class BinaryTree(Tree[T]):
    def __init__(self, comparator: Comparator = default_comparator):
        super().__init__(1, comparator)
        self.root: BinaryNode = self.root

    def _create_node(self, **kwargs: Any) -> BinaryNode[T]:
        return BinaryNode(parent=kwargs.get("parent"))

    def _on_insert(self, input_value: T, value_ix: int, node: BinaryNode[T]) -> None:
        if node.is_root() and node.is_empty():
            node.values.append(input_value)
        else:
            child = BinaryNode(input_value, parent=node)
            node.children[value_ix] = child


if __name__ == "__main__":
    tree = BinaryTree()
    tree.insert(4, 2, 7, 1, 3, 6, 8)

    root: BinaryNode[int] = tree.root
    left = root.left
    right = root.right

    root.rotate(True)
    print("j")
