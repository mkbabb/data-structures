from typing import *

from ..utils import Comparator, bisect, default_comparator

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

    def insert_child(self, ix: int, child: "Node[T]") -> None:
        self.children.insert(ix, child)
        child.parent = self

    def __repr__(self) -> str:
        return f"{self.values}"

    def order(self) -> int:
        return len(self.values) + 1

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def is_root(self) -> bool:
        return self.parent is None

    def is_full(self) -> bool:
        return len(self.values) >= self.tree_order

    def is_empty(self) -> bool:
        return len(self.values) == 0

    def has_children(self) -> bool:
        return len(self.children) > 0

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

    def split(self) -> Tuple[T, "Node[T]"]:
        split_ix = self.tree_order // 2 + 1

        right_children = self.children[split_ix:]
        self.children = self.children[:split_ix]

        right_values = self.values[split_ix:]
        self.values = self.values[:split_ix]

        right_node = self.__class__(
            tree_order=self.tree_order,
            children=right_children,
            values=right_values,
            parent=self.parent,
        )

        return self.values.pop(), right_node

    def rotate(
        self,
        parent_value_ix: int,
        adj_node: "Node[T]",
        go_left: bool,
        rotate_children: bool = True,
    ) -> None:
        parent = self.parent
        new_root = adj_node.values.pop() if go_left else adj_node.values.pop(0)

        new_sibling = parent.values[parent_value_ix]
        parent.values[parent_value_ix] = new_root

        if rotate_children:
            if go_left:
                self.values.insert(0, new_sibling)
            else:
                self.values.append(new_sibling)

            if adj_node.has_children():
                child = adj_node.children.pop() if go_left else adj_node.children.pop(0)
                child.parent = self
                if go_left:
                    self.children.insert(0, child)
                else:
                    self.children.append(child)

    def transfer(
        self,
        parent_value_ix: int,
        adj_node: "Node[T]",
        go_left: bool,
        rotate_children: bool = True,
    ) -> None:
        self.rotate(
            parent_value_ix=parent_value_ix,
            adj_node=adj_node,
            go_left=go_left,
            rotate_children=rotate_children,
        )

    def merge(
        self,
        child_ix: int,
        parent_value_ix: int,
        adj_node: "Node[T]",
        go_left: bool,
        rotate_children: bool = True,
    ) -> None:
        self.values.append(None)

        adj_node.rotate(
            parent_value_ix=parent_value_ix,
            adj_node=self,
            go_left=not go_left,
            rotate_children=rotate_children,
        )
        self.parent.values.pop(parent_value_ix)
        self.parent.children.pop(child_ix)


class BTree(Generic[T]):
    def __init__(self, order: int, comparator: Comparator = default_comparator):
        self.order = order
        self.comparator = comparator
        self.root: Node[T] = self.create_node(tree_order=order)

    def create_node(self, **kwargs: Any) -> Node[T]:
        return Node(**kwargs)

    def _bisect(
        self, arr: List[T], x: T, left: bool = True, negate_found: bool = False
    ) -> int:
        return bisect(arr, x, self.comparator, left, negate_found)

    def _get_node_ix(
        self, node: Node[T], value: T, left: bool = True, negate_found: bool = False
    ):
        return self._bisect(node.values, value, left, negate_found)

    def find(self, input_value: T) -> Tuple[int, Node[T]]:
        def recurse(node: Node[T]) -> Tuple[int, Node[T]]:
            ix = self._get_node_ix(node, input_value, negate_found=True)

            if ix < 0:
                ix = -1 * (ix + 1)
                if node.is_leaf():
                    return ix, node
                else:
                    return recurse(node.children[ix])
            else:
                return ix, node

        return recurse(self.root)

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
    def _get_order(node: Optional[Node[T]]) -> int:
        return -1 if node is None else node.order()

    def _delete_order_1(self, child_ix: int, node: Node[T]):
        if node.is_root():
            self.root = node.children[0]
            self.root.parent = None
        else:
            parent = node.parent

            left_node, right_node = node.siblings(child_ix)
            left_order, right_order = (
                BTree._get_order(left_node),
                BTree._get_order(right_node),
            )

            go_left = left_order >= 2 and right_order <= 2

            parent_value_ix = child_ix - 1 if go_left else child_ix
            adj_node = left_node if go_left else right_node

            if left_order > 2 or right_order > 2:
                node.transfer(
                    parent_value_ix=parent_value_ix, adj_node=adj_node, go_left=go_left
                )
            elif left_order <= 2 or right_order <= 2:
                node.merge(
                    child_ix=child_ix,
                    parent_value_ix=parent_value_ix,
                    adj_node=adj_node,
                    go_left=go_left,
                )
                if parent.order() == 1:
                    grandparent = parent.parent
                    parent_ix = (
                        self._get_node_ix(grandparent, adj_node.values[0])
                        if grandparent is not None
                        else 0
                    )
                    self._delete_order_1(parent_ix, parent)

    def delete(self, input_value: T):
        value_ix, node = self.find(input_value)

        def get_successor_ix() -> Tuple[int, Node[T], T]:
            if node.is_leaf():
                child_ix = (
                    value_ix
                    if node.is_root() or node.order() > 2
                    else self._get_node_ix(node.parent, input_value)
                )
                return child_ix, node, node.values.pop(value_ix)
            else:
                successor = self._successor(value_ix, node)
                value = successor.values[0]

                child_ix = self._get_node_ix(successor.parent, value)

                node.values[value_ix] = value
                return child_ix, successor, successor.values.pop(0)

        child_ix, node, value = get_successor_ix()

        if node.order() == 1 and not node.is_root():
            self._delete_order_1(child_ix, node)
            return value
        else:
            return value

    def _split_insert(self, node: Node[T]) -> Node[T]:
        split_value, right_node = node.split()

        parent = node.parent

        if parent is not None:
            child_ix = self._get_node_ix(parent, split_value)

            parent.insert_child(child_ix + 1, right_node)
            parent.values.insert(child_ix, split_value)
        else:
            children = [node, right_node]
            values = [split_value]
            self.root = parent = self.create_node(
                tree_order=self.order, children=children, values=values
            )

        if parent.is_full():
            return self._split_insert(parent)

        return node

    def _insert(self, input_value: T) -> Node[T]:
        value_ix, node = self.find(input_value)
        node.values.insert(value_ix, input_value)

        if node.is_full():
            return self._split_insert(node)
        else:
            return node

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
