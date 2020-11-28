from typing import *

from ..utils import Comparator, bisect_left, default_comparator

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
        split_ix = self.tree_order // 2 + 1

        right_children = self.children[split_ix:]
        self.children = self.children[:split_ix]

        right_values = self.values[split_ix:]
        self.values = self.values[:split_ix]

        right_node = Node(
            tree_order=self.tree_order,
            children=right_children,
            values=right_values,
            parent=self.parent,
        )

        return self.values.pop(), right_node

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


class BTree(Generic[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        self.order = order
        self.comparator = comparator
        self.root: Node[T] = Node(tree_order=order)

    def _bisect(self, arr: List[T], x: T, negate_found: bool = False) -> int:
        return bisect_left(arr, x, self.comparator, negate_found)

    def _find(self, input_value: T, node: Node[T]) -> Tuple[int, Node[T]]:
        def recurse(node: Node[T]) -> Tuple[int, Node[T]]:
            ix = self._bisect(node.values, input_value, True)

            if ix < 0:
                ix = -1 * (ix + 1)
                if node.is_leaf():
                    return ix, node
                else:
                    return recurse(node.children[ix])
            else:
                return ix, node

        return recurse(node)

    def find(self, input_value: T) -> Tuple[int, Node[T]]:
        return self._find(input_value, self.root)

    @staticmethod
    def _successor(ix: int, node: Node[T]) -> Node[T]:
        if node.is_leaf():
            return node
        else:
            child = node.children[ix + 1]
            while not child.is_leaf():
                child = child.children[0]
            return child

    @staticmethod
    def _rotate(parent_ix: int, node: Node[T], adj_node: Node[T], left: bool) -> None:
        if not node.is_root():
            parent = node.parent

            rotate_ix = -1 if left else 0
            insert_ix = 0 if left else len(node.values)

            new_root = adj_node.values.pop(rotate_ix)

            new_sibling = parent.values[parent_ix]
            parent.values[parent_ix] = new_root

            node.values.insert(insert_ix, new_sibling)

            if adj_node.has_children():
                child = adj_node.children.pop(rotate_ix)
                node.children.insert(insert_ix, child)

    @staticmethod
    def _get_order(node: Optional[Node[T]]) -> int:
        return -1 if node is None else node.order()

    def _delete_order_1(self, ix: int, node: Node[T]):
        if not node.is_root():
            parent = node.parent

            left_node, right_node = node.siblings(ix)
            left_order, right_order = (
                BTree._get_order(left_node),
                BTree._get_order(right_node),
            )
            left = left_order >= 2
            parent_ix = ix - 1 if left else ix
            adj_node = left_node if left else right_node

            def transfer() -> None:
                BTree._rotate(
                    parent_ix=parent_ix,
                    node=node,
                    adj_node=adj_node,
                    left=left,
                )

            def merge() -> None:
                node.values.append(None)

                BTree._rotate(
                    parent_ix=parent_ix,
                    node=adj_node,
                    adj_node=node,
                    left=not left,
                )
                parent.values.pop(parent_ix)
                parent.children.pop(ix)

            if left_order > 2 or right_order > 2:
                transfer()
            elif left_order <= 2 or right_order <= 2:
                merge()
                if parent.order() == 1:
                    self._delete_order_1(parent_ix, parent)
        else:
            self.root = node.children[0]

    def delete(self, input_value: T):
        ix, node = self.find(input_value)

        def get_parent_ix() -> Tuple[Optional[int], Node[T]]:
            if node.is_leaf():
                parent_ix = (
                    None
                    if node.is_root() or node.order() > 2
                    else self._bisect(node.parent.values, input_value)
                )
                return parent_ix, node
            else:
                successor = self._successor(ix, node)
                value = successor.values[0]
                parent_ix = self._bisect(successor.parent.values, value)

                node.values[ix] = value

                return parent_ix, successor

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
            ix = self._bisect(parent.values, split_value)

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
        def recurse(node: Node[T]) -> None:
            if not node.is_leaf():
                for n, child in enumerate(node.children):
                    recurse(child)
                    if n < len(node.values):
                        func(node.values[n])
            else:
                for value in node.values:
                    func(value)

        recurse(self.root)

    def p(self):
        def recurse(node: Node[T], s: str, depth: int = 0):

            if not node.is_leaf():
                t_indent = ("|" + "----" * (depth + 1)) if depth > 0 else ""
                for n, child in enumerate(node.children):

                    s = recurse(child, s, depth + 1)

                    if n < len(node.values):
                        s += t_indent + str(node.values[n]) + "\n"
            else:
                spaces = "    " * depth
                t_indent = spaces + "|---" if depth > 0 else ""

                for value in node.values:
                    s += "|" + t_indent + str(value) + ",\n"

            return s

        return recurse(self.root, "")


if __name__ == "__main__":
    tree: BTree[int] = BTree(4)

    tree.insert(*range(1, 22))

    s = tree.p()

    print(s)
