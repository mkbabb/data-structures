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
        children: Optional[Iterable[Union[T, "Node[T]"]]] = None,
    ):
        self.tree_order = tree_order
        self.children = SparseList(capacity=self.tree_order)

        if children is not None:
            for n, i in enumerate(children):
                self.children.insert(n, i)

    def __repr__(self) -> str:
        return self.children.__repr__()

    def copy(self, copy_children: bool = False) -> "Node[T]":
        children = list(self.children) if copy_children else self.children
        return self.__class__(self.tree_order, children)


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

    @property
    def height(self) -> int:
        return 0 if self.size == 0 else math.floor(math.log(self.size, self.order))

    def path_to(self, root: Node[T], ix: int) -> Node[T]:
        """Start at the root and work down.
        We carve up `ix` into h sections of length `bits`, where h is the height of the tree.
        Example:
            ix = 15; 0b1111
            bits = 3
            tree height = 2

            Sections: [0b1, 0b111] = [1, 7]


            key_1 = (15 << 3*1) & 7 =
            key_0 (leaf key) = (15 << 3*0) & 7 = 7
        """
        node = root

        for i in range(self.height, 0, -1):
            key = (ix >> i * self.bits) & self.mask

            if (child := node.children[key]) is None:
                node.children.insert(key, Node(self.order))
            else:
                node.children[key] = child.copy() if not self.mutation else child

            node = node.children[key]

        return node

    def _append(self, value: T) -> "Trie[T]":
        def get_next_leaf() -> Tuple[Node[T], Node[T]]:
            if self.size < self.order:
                root = self.root.copy(True) if not self.mutation else self.root
                return root, root
            else:
                if is_power_of(self.size, b=self.order):
                    root = Node(self.order, children=[self.root])
                    return root, self.path_to(root, self.size)
                else:
                    root = self.root.copy() if not self.mutation else self.root
                    return root, self.path_to(root, self.size)

        key = self.size & self.mask
        root, node = get_next_leaf()
        node.children.insert(key, value)

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
        root = self.root

        if is_power_of(self.size - 1, b=self.order):
            root = root.children[0]

        return self._create(root)


if __name__ == "__main__":
    tree = Trie(2)
    tree0 = tree.append(0)
    tree1 = tree0.append(1, 2, 3)

    tree2 = tree1.append(4)
    l1 = tree1.root.children
    l2 = tree2.root.children[0].children

    print(l1 is l2)

    # tree2 = tree1.pop()
    print("d")
