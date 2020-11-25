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
        order: int = ORDER,
    ) -> None:
        self.children = children
        for child in children:
            child.parent = self

        self.values = values
        self.parent = parent
        self.order = order

    def __repr__(self) -> str:
        return f"{self.values}"

    def is_leaf(self) -> bool:
        return len(self.children) == 0 or isinstance(self.children[0], int)

    def insert_child(self, ix: int, child: "Node[T]") -> None:
        self.children.insert(ix, child)
        child.parent = self

    def is_full(self) -> bool:
        return len(self.values) >= self.order

    def split(self) -> Tuple[T, "Node[T]"]:
        split_ix = self.order // 2 + 1

        right_children = self.children[split_ix:]
        self.children = self.children[:split_ix]

        right_values = self.values[split_ix:]
        self.values = self.values[:split_ix]

        right_node = Node(
            children=right_children, values=right_values, parent=self.parent
        )

        return self.values.pop(), right_node


class BTree(Generic[T]):
    def __init__(self, order: int, comparator: Optional[Comparator[T]] = None):
        if comparator is None:
            comparator = lambda x, y: -1 if x < y else 1 if x > y else 0

        self.order = order
        self.comparator = comparator
        self.root: Node[T] = Node(order=self.order)

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

    def _successor(node: Node[T]):
        while not node.is_leaf():
            node = node.children[0]
        return node

    def delete(self, input_value: T):
        parent_ix, ix, node = self.find(input_value)
        successor = self._successor(node)
        print("help")

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

tree.for_each(lambda x: print(x))
# tree.delete(18)