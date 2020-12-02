from typing import TypeVar
import math
from typing import *

from ..utils.utils import Comparator, bisect, default_comparator
from .tree import Tree, TreeNode

T = TypeVar("T")


class BinaryNode(TreeNode[T]):
    def __init__(
        self,
        value: Optional[T] = None,
        left: Optional["BinaryNode[T]"] = None,
        right: Optional["BinaryNode[T]"] = None,
        parent: Optional["BinaryNode[T]"] = None,
        **kwargs
    ) -> None:
        super().__init__(2, [left, right], None, parent)
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
