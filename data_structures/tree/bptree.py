from typing import *

from ..utils import Comparator, bisect_left, bisect_right, _bisect, default_comparator

T = TypeVar("T")


class Node(Generic[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[List["Node[T]"]] = None,
        values: Optional[List[T]] = None,
        parent: Optional["Node[T]"] = None,
    ) -> None:
        self.tree_order = tree_order

        if children is None:
            children = []
        if values is None:
            values = []

        self.children = children
        for child in children:
            child.parent = self

        self.values = values
        self.parent = parent

        self.next = None
        self.previous = None

    def __repr__(self) -> str:
        return f"{self.values}"

    def order(self) -> int:
        return len(self.values) + 1

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def is_root(self) -> bool:
        return self.parent is None

    def insert_child(self, ix: int, child: "Node[T]") -> None:
        self.children.insert(ix, child)
        child.parent = self

    def is_full(self) -> bool:
        return len(self.values) >= self.tree_order

    def is_empty(self) -> bool:
        return len(self.values) == 0

    def has_children(self) -> bool:
        return len(self.children) > 0

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

    def get_child(self, ix: int) -> Optional["Node[T]"]:
        if self.parent is not None:
            if ix >= 0 and ix < len(self.parent.children):
                return self.parent.children[ix]
        return None

    def siblings(
        self, parent_ix: int
    ) -> Tuple[Optional["Node[T]"], Optional["Node[T]"]]:
        left_ix = parent_ix - 1
        right_ix = parent_ix + 1

        return self.get_child(left_ix), self.get_child(right_ix)


class BPTree(Generic[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        self.order = order
        self.comparator = comparator
        self.root: Node[T] = Node(tree_order=order)

    def _bisect(self, arr: List[T], x: T, left: bool = True) -> int:
        return _bisect(arr, x, self.comparator, left)

    def _bisect_positive(self, arr: List[T], x: T, left: bool = True) -> int:
        ix = self._bisect(arr, x, left)
        return -1 * (ix + 1) if ix < 0 else ix

    def _find(self, input_value: T, node: Node[T]) -> Tuple[int, Node[T]]:
        def recurse(node: Node[T]):
            ix = self._bisect_positive(node.values, input_value, node.is_leaf())

            if node.is_leaf():
                return ix, node
            else:
                child = node.children[ix]
                return recurse(child)

        return recurse(node)

    def find(self, input_value: T) -> Tuple[int, Node[T]]:
        return self._find(input_value, self.root)

    @staticmethod
    def _successor(ix: int, node: Node[T]) -> Node[T]:
        if node.is_leaf():
            return node
        else:
            node = node.children[ix + 1]

            while not node.is_leaf():
                node = node.children[0]

            return node

    @staticmethod
    def _rotate(
        parent_ix: int,
        node: Node[T],
        adj_node: Node[T],
        has_left: bool,
        rotate_children: bool = False,
    ) -> None:
        parent = node.parent
        new_root = adj_node.values.pop() if has_left else adj_node.values.pop(0)

        new_sibling = parent.values[parent_ix]
        parent.values[parent_ix] = new_root

        if rotate_children:
            if has_left:
                node.values.insert(0, new_sibling)
            else:
                node.values.append(new_sibling)

            if adj_node.has_children():
                child = (
                    adj_node.children.pop() if has_left else adj_node.children.pop(0)
                )
                child.parent = node
                if has_left:
                    node.children.insert(0, child)
                else:
                    node.children.append(child)

    @staticmethod
    def _get_order(node: Optional[Node[T]]) -> int:
        return -1 if node is None else node.order()

    def _delete_order_1(self, ix: int, node: Node[T]):
        if node.is_root():
            self.root = node.children[0]
        else:
            parent = node.parent

            left_node, right_node = node.siblings(ix)
            left_order, right_order = (
                BPTree._get_order(left_node),
                BPTree._get_order(right_node),
            )
            has_left = left_order >= 2 and right_order < 2
            parent_ix = ix - 1 if has_left else ix
            adj_node = left_node if has_left else right_node

            def transfer() -> None:
                BPTree._rotate(
                    parent_ix=parent_ix,
                    node=node,
                    adj_node=adj_node,
                    has_left=has_left,
                    rotate_children=True,
                )

            def merge() -> None:
                node.values.append(None)

                BPTree._rotate(
                    parent_ix=parent_ix,
                    node=adj_node,
                    adj_node=node,
                    has_left=not has_left,
                    rotate_children=not node.is_leaf(),
                )

                parent.values.pop(parent_ix)
                parent.children.pop(ix)

            if left_order > 2 or right_order > 2:
                transfer()
            elif left_order <= 2 or right_order <= 2:
                merge()
                if parent.order() == 1:
                    grandparent = parent.parent

                    if grandparent is not None:
                        rotate_ix = len(adj_node.values) - 1 if has_left else 0
                        ix = self._bisect_positive(
                            grandparent.values, adj_node.values[rotate_ix]
                        )
                    self._delete_order_1(ix, parent)

    def delete(self, input_value: T):
        ix, node = self.find(input_value)

        def get_parent_ix() -> Tuple[Optional[int], Node[T]]:
            if node.is_leaf():
                parent_ix = (
                    None
                    if node.is_root() or node.order() > 2
                    else self._bisect_positive(node.parent.values, input_value, False)
                )
                return parent_ix, node
            else:
                successor = self._successor(ix, node)
                value = successor.values[0]
                parent_ix = self._bisect_positive(successor.parent.values, value)

                node.values[ix] = value

                return parent_ix, successor

        previous, next = node.previous, node.next

        if previous is not None:
            previous.next = next

            if next is not None:
                next.previous = previous

        parent_ix, node = get_parent_ix()
        value = node.values.pop(ix)

        if node.order() == 1:
            self._delete_order_1(parent_ix, node)
            return value
        else:
            return value

    def _split_insert(self, node: Node[T]):
        split_value, right_node = node.split()

        parent = node.parent
        if parent is not None:
            ix = self._bisect_positive(parent.values, split_value)

            parent.insert_child(ix + 1, right_node)
            parent.values.insert(ix, split_value)
        else:
            children = [node, right_node]
            values = [split_value]
            self.root = parent = Node(
                tree_order=self.order, children=children, values=values
            )

        if parent.is_full():
            self._split_insert(parent)

    def _insert(self, input_value: T) -> None:
        ix, node = self.find(input_value)
        node.values.insert(ix, input_value)

        if node.is_full():
            self._split_insert(node)

    def insert(self, *input_values: T) -> None:
        for input_value in input_values:
            self._insert(input_value)

    def for_each(self, func: Callable[[T], None]) -> None:
        min_node = self._successor(-1, self.root)
        min_node.next
