from typing import *
from data_structures.tree.binary_tree import BinaryTree

from src.data_structures.tree import Tree, TreeNode, BinaryNode
from src.data_structures.utils.utils import Comparator, bisect, default_comparator


T = TypeVar("T")

class AVLTreeNode(BinaryNode[T]):
    def __init__(
        self,
        height: int,
        value: Optional[T] = None,
        left: Optional["BinaryNode[T]"] = None,
        right: Optional["BinaryNode[T]"] = None,
        parent: Optional["BinaryNode[T]"] = None,
    ) -> None:
        self.height = height
        super().__init__(tree_order=1, children=[left, right], parent=parent)
        
        if value is not None:
            self.values.append(value)

    @property
    def height(self) -> int:
        return self.height

    @height.setter
    def height(self, other = int):
        self.height = other


class AVLTree(BinaryTree[T]):
    def __init__(self, comparator: Comparator = default_comparator):
        super().__init__(1, comparator)

    def _on_insert(self, input_value: T, value_ix: int, node: BinaryNode[T]) -> None:
        super()._on_insert(1, input_value, value_ix, node)

    def compute_height(self):
        return

    def rebalance(self):
        return

    def _on_delete(self, child_ix: int, node: TreeNode[T], value: T) -> None:
        return