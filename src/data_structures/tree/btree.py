import math
from typing import *

from ..utils.utils import Comparator, bisect, default_comparator
from .tree import Tree, TreeNode

T = TypeVar("T")


class BTreeNode(TreeNode[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[List["BTreeNode[T]"]] = None,
        values: Optional[List[T]] = None,
        parent: Optional["BTreeNode[T]"] = None,
    ) -> None:
        super().__init__(tree_order, children, values, parent)
        self.min_order = int(math.ceil(tree_order / 2))

    def is_min_internal_order(self) -> bool:
        return self.order() < self.min_order

    def is_min_leaf_order(self) -> bool:
        return self.order() < self.min_order - 1

    def split(self) -> Tuple[T, "BTreeNode[T]"]:
        value_ix = int(math.floor(self.tree_order / 2))
        child_ix = int(math.ceil((self.tree_order + 1) / 2))

        right_children = self.children[child_ix:]
        self.children = self.children[:child_ix]

        split_value = self.values[value_ix]

        right_values = self.values[value_ix + 1 :]
        self.values = self.values[:value_ix]

        right_node = self.__class__(
            tree_order=self.tree_order,
            children=right_children,
            values=right_values,
            parent=self.parent,
        )

        return split_value, right_node

    def transfer(
        self,
        parent_value_ix: int,
        adj_node: "BTreeNode[T]",
        go_left: bool,
        rotate_children: bool = True,
    ) -> None:
        self.rotate(
            parent_value_ix=parent_value_ix,
            adj_node=adj_node,
            go_left=go_left,
            rotate_children=rotate_children,
        )
        return self

    def merge(
        self, child_ix: int, parent_value_ix: int, adj_node: "BTreeNode[T]", go_left: bool
    ) -> "BTreeNode[T]":
        value = self.parent.values.pop(parent_value_ix)

        if go_left:
            self.values = adj_node.values + [value] + self.values
            self.children = adj_node.children + self.children
            self.parent.children.pop(child_ix - 1)
        else:
            self.values += [value] + adj_node.values
            self.children += adj_node.children
            self.parent.children.pop(child_ix + 1)

        return self


class BTree(Tree[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        super().__init__(order, comparator)

    def create_node(self, **kwargs: Any) -> BTreeNode[T]:
        return BTreeNode(**kwargs)

    def _delete_min_order(self, child_ix: int, node: BTreeNode[T]):
        if node.is_root():
            self.root = node.children[0]
            self.root.parent = None
        else:
            parent = node.parent
            left_node, right_node = node.siblings(child_ix)

            if left_node is not None and not left_node.is_min_internal_order():
                node.transfer(
                    parent_value_ix=child_ix - 1, adj_node=left_node, go_left=True
                )
            elif right_node is not None and not right_node.is_min_internal_order():
                node.transfer(
                    parent_value_ix=child_ix, adj_node=right_node, go_left=False
                )
            else:
                if left_node is not None:
                    node.merge(
                        child_ix=child_ix,
                        parent_value_ix=child_ix - 1,
                        adj_node=left_node,
                        go_left=True,
                    )
                elif right_node is not None:
                    node.merge(
                        child_ix=child_ix,
                        parent_value_ix=child_ix,
                        adj_node=right_node,
                        go_left=False,
                    )
                for child in node.children:
                    child.parent = node

                if parent.order() == 0 or (
                    not parent.is_root() and parent.is_min_leaf_order()
                ):
                    grandparent = parent.parent
                    parent_ix = (
                        self._get_node_ix(grandparent, node.values[0])
                        if grandparent is not None
                        else 0
                    )
                    self._delete_min_order(parent_ix, parent)

    def _on_delete(self, child_ix: int, node: BTreeNode[T], value: T) -> None:
        if node.is_min_leaf_order() and not node.is_root():
            self._delete_min_order(child_ix, node)
            return value
        else:
            return value

    def _split_insert(self, node: BTreeNode[T]) -> BTreeNode[T]:
        split_value, right_node = node.split()

        parent = node.parent

        if not node.is_root():
            child_ix = self._get_node_ix(parent, split_value)
            parent.children.insert(child_ix + 1, right_node)
            parent.values.insert(child_ix, split_value)
        else:
            children = [node, right_node]
            values = [split_value]
            self.root = parent = self.create_node(
                tree_order=self.order,
                children=children,
                values=values,
                parent=parent,
            )

        if parent.is_full():
            return self._split_insert(parent)

        return node

    def _on_insert(self, value_ix: int, node: BTreeNode[T]) -> None:
        if node.is_full():
            self._split_insert(node)
