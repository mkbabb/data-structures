from typing import *
from data_structures.tree.binary_tree import BinaryTree

from src.data_structures.tree import Tree, TreeNode, BinaryNode
from src.data_structures.utils.utils import Comparator, bisect, default_comparator


T = TypeVar("T")

#might need avl tree node that
#has an additional property of height
class AVLTree(Tree[T]):
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

    def _on_insert(self, input_value: T, value_ix: int, node: BinaryNode[T]) -> None:
        if node.is_root() and node.is_empty():
            node.values.append(input_value)
        else:
            child = BinaryNode(input_value, parent=node)
            node.children[value_ix] = child
            self.compute_height()


    def compute_height(self):
        return

    def rebalance(self):
        return

    def _on_delete(self, child_ix: int, node: TreeNode[T], value: T) -> None:
        return