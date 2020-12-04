from typing import *
from data_structures.tree.binary_tree import BinaryTree

from src.data_structures.tree import Tree, TreeNode, BinaryNode
from src.data_structures.utils.utils import Comparator, bisect, default_comparator


T = TypeVar("T")

#might need avl tree node that
#has an additional property of height
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