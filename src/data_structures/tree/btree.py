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


# arr = [1, 2, 9, 10]

# t = bisect_left(arr, 11)

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
        return len(self.children) == 0 or isinstance(self.children[0], int)

    def insert_child(self, ix: int, child: "Node[T]") -> None:
        self.children.insert(ix, child)
        child.parent = self

    def is_full(self) -> bool:
        return len(self.values) >= self.tree_order

    def is_empty(self) -> bool:
        return len(self.values) == 0

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

    def find(self, input_value: T) -> Tuple[int, int, Node[T]]:
        def recurse(node: Node[T], parent_ix: int) -> Tuple[int, int, Node[T]]:
            ix = bisect_left(node.values, input_value, self.comparator)

            if ix < 0:
                ix = -1 * (ix + 1)
                if node.is_leaf():
                    return parent_ix, ix, node
                else:
                    child = node.children[ix]
                    return recurse(child, ix)
            else:
                return parent_ix, ix, node

        return recurse(self.root, -1)

    @staticmethod
    def _successor(node: Node[T]) -> Tuple[int, Node[T]]:
        ix = len(node.children) - 1
        node = node.children[ix]

        while not node.is_leaf():
            node = node.children[ix]
            ix = 0

        return ix, node

    @staticmethod
    def _rotate(rotate_ix: int, node: Node[T], left: bool) -> Tuple[Node[T], T]:
        parent = node.parent

        new_value = node.values.pop() if left else node.values.pop(0)
        rotate_child = None
        if len(node.children) > 0:
            rotate_child = node.children.pop() if left else node.children.pop(0)

        old_value = parent.values[rotate_ix]
        parent.values[rotate_ix] = new_value

        return rotate_child, old_value

    @staticmethod
    def _get_order(node: Optional[Node[T]]) -> int:
        return -1 if node is None else node.order()

    @staticmethod
    def _delete_order_1(parent_ix: int, node: Node[T]):
        parent = node.parent

        if parent is not None:
            left_node, right_node = node.siblings(parent_ix)
            left_order, right_order = (
                BTree._get_order(left_node),
                BTree._get_order(right_node),
            )
            left = left_order >= 2
            rotate_ix = parent_ix - 1 if left else parent_ix

            def transfer() -> None:
                child, value = BTree._rotate(
                    rotate_ix=rotate_ix,
                    node=left_node if left else right_node,
                    left=left,
                )
                node.values.append(value)

            def merge() -> None:
                value = parent.values.pop(rotate_ix)
                parent.children.pop(parent_ix)
                if left:
                    left_node.values.append(value)
                else:
                    right_node.values.insert(0, value)

            if left_order > 2 or right_order > 2:
                transfer()
            elif left_order <= 2 or right_order <= 2:
                merge()
                if parent.order() == 1:
                    BTree._delete_order_1(parent_ix, parent)

    def delete(self, input_value: T):
        parent_ix, ix, node = self.find(input_value)

        if node.is_leaf():
            node.values.pop(ix)
        else:
            parent_ix, successor = self._successor(node)
            node.values[ix] = successor.values.pop(0)
            node = successor

        if node.order() == 1:
            self._delete_order_1(parent_ix, node)

    def _split_insert(self, parent_ix: int, node: Node[T]):
        split_value, right_node = node.split()

        parent = node.parent

        if parent is not None:
            parent.insert_child(parent_ix + 1, right_node)
            parent.values.insert(parent_ix, split_value)
        else:
            children = [node, right_node]
            values = [split_value]
            self.root = parent = Node(children=children, values=values)

        if parent.is_full():
            self._split_insert(parent_ix, parent)

    def _insert(self, input_value: T) -> None:
        parent_ix, ix, node = self.find(input_value)
        node.values.insert(ix, input_value)

        if node.is_full():
            self._split_insert(parent_ix, node)

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


# node1 = Node()
# node1.values = [10, 20, 30]

# node2 = Node()
# node2.values = [5]

# node3 = Node()
# node3.values = [17]

# node4 = Node()
# node4.values = [22, 24, 29]
# node4.children = [1, 2, 3, 4, 5]

# node5 = Node()
# node5.values = [31]


# node1.children = [node2, node3, node4, node5]
# for node in node1.children:
#     node.parent = node1

tree: BTree[int] = BTree(ORDER)
# tree.root = node1

tree.insert(*range(1, 23))

tree.delete(1)
tree.delete(4)
tree.delete(7)

tree.delete(2)
tree.delete(5)
tree.delete(6)
# tree.delete(3)
# tree.delete(6)
