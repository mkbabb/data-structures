from typing import *
from data_structures.tree.binary_tree import BinaryTree

from src.data_structures.tree import Tree, TreeNode, BinaryNode
from src.data_structures.utils.utils import Comparator, bisect, default_comparator


T = TypeVar("T")

class AVLTreeNode(BinaryNode[T]):
    def __init__(
        self,
        value: Optional[T] = None,
        left: Optional["BinaryNode[T]"] = None,
        right: Optional["BinaryNode[T]"] = None,
        parent: Optional["BinaryNode[T]"] = None,
    ) -> None:
        self.height = 1
        self.bf = 0
        super().__init__(tree_order=1, children=[left, right], parent=parent)
        
        if value is not None:
            self.values.append(value)

    @property
    def height(self) -> int:
        return self.height

    @height.setter
    def height(self, other = int):
        self.height = other

    @property
    def balance_factor(self) -> int:
        return self.balance_factor

    @balance_factor.setter
    def balance_factor(self, other = int):
        self.bf = other


class AVLTree(BinaryTree[T]):
    def __init__(self, comparator: Comparator = default_comparator):
        super().__init__(1, comparator)

    def _on_insert(self, input_value: T, value_ix: int, node: BinaryNode[T]) -> None:
        super()._on_insert(1, input_value, value_ix, node)
        node.height = max(node.left.height() - node.right.height()) + 1
        node.bf = node.left.height() - node.right.height()
        self.rebalance()

    #return the index where you need to rebalance
    def compute_height(self, AVLTreeNode = AVLTreeNode[T]) -> int:
        if self is None:
            return 0
        else:
            return AVLTreeNode.height()

    def update_heights(self) -> None:
        if self is None:
            self.height = -1
        else:
            return

    def rebalance(self) -> None:
        if self.compute_heights() is not -1:
            return
        #balance if needed
        self.update_heights()

    def _delete(self, input_value: T) -> None:
        super()._delete(self, input_value)
        self.rebalance()
