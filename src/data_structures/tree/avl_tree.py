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


class AVLTree(BinaryTree[T]):
    def __init__(self, comparator: Comparator = default_comparator):
        super().__init__(1, comparator)

    def _on_insert(self, input_value: T, value_ix: int, node: AVLTreeNode[T]) -> None:
        super()._on_insert(1, input_value, value_ix, node)
        node.height = max(node.left.height - node.right.height) + 1
        node.bf = node.left.height - node.right.height
        self.rebalance(node)

    def update_height(self) -> None:
        return

    def update_bf(self) -> None:
        return

    def rebalance(self, node: AVLTreeNode[T]) -> None:
        tree_changed = False

        if node.bf == -2:
            tree_changed = True
            if node.right.bf > 0: #right left rotate
                node.right = super().rotate(False)
                super().rotate(True)
            else:
                super().rotate(True)

        elif node.bf == 2:
            tree_changed = True
            if node.left.bf < 0:
                node.left = super().rotate(True) #left right rotate
                super().rotate(False)
            else:
                super().rotate(False)

        if tree_changed:
            self.update_height()
            self.update_bf()

    def _on_delete(self, child_ix: int, node: TreeNode[T], value: T) -> None:
        self.rebalance(node.parent)
        self.update_height()
        self.update_bf()
