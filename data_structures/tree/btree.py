from typing import *


T = TypeVar("T")
Comparator = Callable[[T, T], int]


def bisect_left(arr: List[T], x: T, comparator: Optional[Comparator[T]] = None) -> int:
    if comparator is None:
        comparator = lambda x, y: -1 if x < y else 1 if x > y else 0

    def recurse(low: int, high: int) -> int:
        midpoint = (high + low) // 2

        if low <= high:
            midvalue = arr[midpoint]

            comp = comparator(x, midvalue)

            if comp < 0:
                return recurse(low, midpoint - 1)
            elif comp > 0:
                return recurse(midpoint + 1, high)
            else:
                return midpoint
        else:
            return -1 * (low + 1)

    return recurse(0, len(arr) - 1)


ORDER = 4


class Node(Generic[T]):
    def __init__(
        self,
        children: List["Node[T]"] = [],
        values: List[T] = [],
        parent: Optional["Node[T]"] = None,
        tree_order: int = ORDER,
    ) -> None:
        self.children = children
        for child in children:
            child.parent = self

        self.values = values
        self.parent = parent
        self.tree_order = tree_order

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
            children=right_children, values=right_values, parent=self.parent
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
    def __init__(self, order: int, comparator: Optional[Comparator[T]] = None):
        if comparator is None:
            comparator = lambda x, y: -1 if x < y else 1 if x > y else 0

        self.order = order
        self.comparator = comparator
        self.root: Node[T] = Node()

    def _bisect(self, arr: List[T], x: T) -> int:
        return bisect_left(arr, x, self.comparator)

    def _bisect_positive(self, arr: List[T], x: T) -> int:
        ix = self._bisect(arr, x)
        return -1 * (ix + 1) if ix < 0 else ix

    def _find(self, input_value: T, node: Node[T]) -> Tuple[int, Node[T]]:
        def recurse(node: Node[T]):
            ix = self._bisect(node.values, input_value)

            if ix < 0:
                ix = -1 * (ix + 1)
                if node.is_leaf():
                    return ix, node
                else:
                    child = node.children[ix]
                    return recurse(child)
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
            node = node.children[ix + 1]

            while not node.is_leaf():
                node = node.children[0]

            return node

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
        parent = node.parent

        if parent is not None:

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

    def delete(self, input_value: T):
        ix, node = self.find(input_value)

        def get_parent_ix() -> Tuple[Optional[int], Node[T]]:
            if node.is_leaf():
                parent_ix = (
                    None
                    if node.is_root() or node.order() > 2
                    else self._bisect_positive(node.parent.values, input_value)
                )
                return parent_ix, node
            else:
                successor = self._successor(ix, node)
                value = successor.values[0]
                parent_ix = self._bisect_positive(successor.parent.values, value)

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
            ix = self._bisect_positive(parent.values, split_value)

            parent.insert_child(ix + 1, right_node)
            parent.values.insert(ix, split_value)
        else:
            children = [node, right_node]
            values = [split_value]
            self.root = parent = Node(children=children, values=values)

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
    # root = Node()
    # root.values = [9, 20, 30]

    # node1 = Node()
    # node1.values = [5, 6]

    # node2 = Node()
    # node2.values = [10]

    # node3 = Node()
    # node3.values = [21, 22, 23]
    # node3.children = [1, 2, 3, 4]

    # node4 = Node()
    # node4.values = [31, 32, 33]

    # root.children = [node1, node2, node3, node4]
    # for node in root.children:
    #     node.parent = root

    tree: BTree[int] = BTree(ORDER)

    # tree.root = root
    # tree.p()

    # tree.insert(24)
    # tree.delete(10)
    # tree.delete(5)

    tree.insert(*range(1, 22))
    # tree.for_each(print)

    tree.delete(1)
    tree.delete(4)
    tree.delete(7)

    tree.delete(3)
    tree.delete(5)
    tree.delete(2)

    s = tree.p()

    print(s)