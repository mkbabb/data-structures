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
        **kwargs: Any
    ) -> None:
        super().__init__(tree_order=1, children=[left, right], parent=parent)
        if value is not None:
            self.values.append(value)

    def is_leaf(self) -> bool:
        return self.left() is None and self.right() is None

    def left(self) -> Optional["BinaryNode[T]"]:
        return self.children[0]

    def right(self) -> Optional["BinaryNode[T]"]:
        return self.children[1]

    def value(self) -> T:
        return self.values[0]


class BinaryTree(Tree[T]):
    def __init__(self, comparator: Comparator = default_comparator):
        super().__init__(2, comparator)

    def create_node(self, **kwargs: Any) -> BinaryNode[T]:
        return BinaryNode(**kwargs)

    def _on_insert(self, input_value: T, value_ix: int, node: BinaryNode[T]) -> None:
        if node.is_root() and node.is_empty():
            node.values.append(input_value)
        else:
            child = BinaryNode(input_value, parent=node)
            node.children[value_ix] = child


if __name__ == "__main__":
    tree = BinaryTree()
    tree.insert(1, 2, 3, 4, 5, 6)
    print(tree.root)