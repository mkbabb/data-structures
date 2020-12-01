from typing import *

from ..utils import Comparator, bisect, default_comparator
from .btree import BTreeNode, BTree
import math

T = TypeVar("T")


class BPTreeNode(BTreeNode[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[List["BTreeNode[T]"]] = None,
        values: Optional[List[T]] = None,
        parent: Optional["BTreeNode[T]"] = None,
    ) -> None:
        super().__init__(tree_order, children, values, parent)
        self.next = None
        self.previous = None

    def split(self) -> Tuple[T, "BTreeNode[T]"]:
        value_ix = int(math.floor(self.tree_order / 2))
        child_ix = int(math.ceil((self.tree_order + 1) / 2))

        right_children = self.children[child_ix:]
        self.children = self.children[:child_ix]

        # split_value = self.values[value_ix]

        right_values = self.values[value_ix:]
        self.values = self.values[:value_ix]

        right_node = self.__class__(
            tree_order=self.tree_order,
            children=right_children,
            values=right_values,
            parent=self.parent,
        )

        if right_node.is_leaf():
            self.next = right_node
            right_node.previous = self

        split_value = right_values[0] if right_node.is_leaf() else right_values.pop(0)

        return split_value, right_node


class BPTree(BTree[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        super().__init__(order, comparator)

    def create_node(self, **kwargs: Any) -> BTreeNode[T]:
        return BPTreeNode(**kwargs)

    def _get_node_ix(
        self,
        node: BTreeNode[T],
        value: T,
        left: bool = False,
        negate_found: bool = False,
    ):
        return self._bisect(node.values, value, left=left, negate_found=negate_found)

    def find(self, input_value: T) -> Tuple[int, BTreeNode[T]]:
        def recurse(node: BTreeNode[T]):
            ix = self._get_node_ix(
                node, input_value, left=node.is_leaf(), negate_found=False
            )

            if node.is_leaf():
                return ix, node
            else:
                child = node.children[ix]
                return recurse(child)

        return recurse(self.root)

    def for_each(self, func: Callable[[T], None]) -> None:
        node = self._successor(-1, self.root)

        while True:
            for value in node.values:
                func(value)

            node = node.next

            if node is None:
                break
