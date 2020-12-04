import math
from typing import *

from typing_extensions import *

from src.data_structures.utils.utils import is_power_of
from src.data_structures.list.vector import Vector
from src.data_structures.list.sparse_list import SparseList

from contextlib import contextmanager

T = TypeVar("T")


class Node(Generic[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[Iterable["Node[T]"]] = None,
        values: Optional[Iterable[T]] = None,
        parent: Optional["Node[T]"] = None,
    ):
        self.tree_order = tree_order
        self.children = SparseList(capacity=self.tree_order)
        self.values = SparseList(capacity=self.tree_order)
        self.parent = parent

        if children is not None:
            for n, i in enumerate(children):
                if i is not None:
                    i.parent = self
                self.children.insert(n, i)

        if values is not None:
            for n, i in enumerate(values):
                self.values.insert(n, i)

    def __repr__(self) -> str:
        return self.values.__repr__()

    def copy(self, copy_values: bool = False) -> "Node[T]":
        values = self.values if not copy_values else list(self.values)
        return self.__class__(
            tree_order=self.tree_order,
            children=self.children,
            values=values,
            parent=self.parent,
        )


class Trie(Generic[T]):
    def __init__(self, order: int):
        self.order = order
        self.root = Node[T](order)
        self.size = 0
        self.bits = int(math.log2(order))
        self.mask = self.order - 1
        self.mutation = False

    def _create(self, root: Optional[Node[T]], size: Optional[int] = None) -> "Trie[T]":
        out = self.__class__(self.order)
        out.root = root if root is not None else self.root
        out.size = size if size is not None else self.size
        return out

    @staticmethod
    @contextmanager
    def mutate(tree: "Trie[T]") -> Generator["Trie[T]", None, None]:
        try:
            tree.mutation = True
            yield tree
        finally:
            tree.mutation = False

    @staticmethod
    def get_tree_height(size: int, node_size: int) -> int:
        return 0 if size == 0 else math.floor(math.log(size, node_size))

    @property
    def height(self) -> int:
        return self.get_tree_height(self.size, self.order)

    def slice_key(self, key: int, depth: int = 0) -> int:
        return (key >> depth * self.bits) & self.mask

    def path_to(self, key: int, node: Node[T], height: int) -> Node[T]:
        """Start at the root and work down.
        We carve up `key` into h sections of length `bits`, where h is the height of the tree.
        Example:
            ix = 15; 0b1111
            bits = 3
            tree height = 2

            Sections: [0b1, 0b111] = [1, 7]


            key_1 = (15 << 3*1) & 7 =
            key_0 (leaf key) = (15 << 3*0) & 7 = 7
        """

        for i in range(height, 0, -1):
            ix = self.slice_key(key, i)

            if (child := node.children[ix]) is None:
                node.children.insert(ix, Node(self.order, parent=node))
            else:
                node.children[ix] = child.copy() if not self.mutation else child

            node = node.children[ix]

        return node

    def _append(self, value: T) -> "Trie[T]":
        key = self.size
        height = self.height

        def get_next_leaf() -> Tuple[Node[T], Node[T]]:
            if key < self.order:
                root = self.root.copy(True) if not self.mutation else self.root
                return root, root
            else:
                if is_power_of(key, b=self.order):
                    root = Node(self.order, children=[self.root])
                    return root, self.path_to(key, root, height)
                else:
                    root = self.root.copy() if not self.mutation else self.root
                    return root, self.path_to(key, root, height)

        root, node = get_next_leaf()
        node.values.insert(key & self.mask, value)

        if self.mutation:
            self.root = root
            self.size += 1
            return self
        else:
            return self._create(root, self.size + 1)

    def append(self, *values: T) -> "Trie[T]":
        for value in values:
            self = self._append(value)
        return self

    def pop(self) -> "Trie[T]":
        root = self.root.copy() if not self.mutation else self.root
        key = self.size - 1
        height = self.get_tree_height(key, self.order)

        if is_power_of(key, b=self.order):
            root = root.children[0]
        else:
            node = self.path_to(key, root, height)

            if key & self.mask == 0:
                node.parent.children.pop(self.slice_key(key, 1))
            else:
                node.values.pop(key & self.mask)

        return self._create(root, key)


if __name__ == "__main__":
    tree = Trie(4)
    tree0 = tree.append(0)
    tree1 = tree0.append(1, 2, 3)

    tree2 = tree1.append(4, 5, 6, 7, 8, 9)
    l1 = tree1.root.children
    l2 = tree2.root.children[0].children

    print(l1 is l2)

    tree3 = tree2.pop().pop().pop()
    tree3.append(7)
    print("d")
