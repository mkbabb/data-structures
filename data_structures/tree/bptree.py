from typing import *

from ..utils import Comparator, bisect, default_comparator
from .btree import Node, BTree

T = TypeVar("T")


class BPTreeNode(Node[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[List["Node[T]"]] = None,
        values: Optional[List[T]] = None,
        parent: Optional["Node[T]"] = None,
    ) -> None:
        super().__init__(tree_order, children, values, parent)

    def split(self) -> Tuple[T, "Node[T]"]:
        split_children_ix = (self.tree_order + 1) // 2
        split_values_ix = self.tree_order // 2

        right_children = self.children[split_children_ix:]
        self.children = self.children[:split_children_ix]

        right_values = self.values[split_values_ix:]
        self.values = self.values[:split_values_ix]

        right_node = Node(
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

    def merge(
        self, child_ix: int, parent_value_ix: int, adj_node: "Node[T]", go_left: bool
    ) -> None:
        self.values.append(None)

        adj_node.rotate(
            parent_value_ix=parent_value_ix,
            adj_node=self,
            go_left=not go_left,
            rotate_children=not self.is_leaf(),
        )

        self.parent.values.pop(parent_value_ix)
        self.parent.children.pop(child_ix)


class BPTree(BTree[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        super().__init__(order, comparator)

    def create_node(self, **kwargs: Any) -> Node[T]:
        return BPTreeNode(**kwargs)

    def find(self, input_value: T) -> Tuple[int, Node[T]]:
        def recurse(node: Node[T]):
            ix = self._bisect(
                node.values, input_value, left=node.is_leaf(), negate_found=False
            )

            if node.is_leaf():
                return ix, node
            else:
                child = node.children[ix]
                return recurse(child)

        return recurse(self.root)

    def insert(self, *input_values: T) -> None:
        for input_value in input_values:
            node = self._insert(input_value)

    def for_each(self, func: Callable[[T], None]) -> None:
        min_node = self._successor(-1, self.root)
        min_node.next
