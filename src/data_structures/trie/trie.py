import math
from typing import *

from typing_extensions import *

from src.data_structures.utils.utils import is_power_of
from src.data_structures.list.vector import Vector
from src.data_structures.list.sparse_list import SparseList
from src.data_structures.tree.tree import TreeNode

from contextlib import contextmanager

T = TypeVar("T")


class TrieNode(Generic[T]):
    def __init__(
        self,
        tree_order: int,
        children: Optional[SparseList["TrieNode[T]"]] = None,
        parent: Optional["TrieNode[T]"] = None,
    ):
        self.tree_order = tree_order
        self.children = children
        self.parent = parent

    def __repr__(self) -> str:
        return f"{self.children}"

    def copy(self) -> "TrieNode[T]":
        return self.__class__(
            tree_order=self.tree_order,
            children=(
                self.children.copy() if self.children is not None else self.children
            ),
            parent=self.parent,
        )


class TrieLeafNode(TrieNode[T]):
    def __init__(
        self,
        tree_order: int,
        values: Optional[SparseList[T]] = None,
        parent: Optional["TrieNode[T]"] = None,
    ) -> None:
        super().__init__(tree_order=tree_order, children=None, parent=parent)
        self.values = values if values is not None else SparseList(self.tree_order)

    def __repr__(self) -> str:
        return f"{self.values}"

    def copy(self) -> "TrieLeafNode[T]":
        return self.__class__(
            tree_order=self.tree_order,
            values=self.values.copy(),
            parent=self.parent,
        )


class Trie(Generic[T]):
    def __init__(self, order: int):
        self.order = order
        self.root: TrieNode[T] = TrieLeafNode[T](order)
        self.size = 0
        self.bits = int(math.log2(order))
        self.mask = self.order - 1
        self.mutation = False

    def _create(
        self, root: Optional[TrieNode[T]], size: Optional[int] = None
    ) -> "Trie[T]":
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

    def path_to(
        self, ix: int, node: TrieNode[T], height: Optional[int] = None
    ) -> TrieLeafNode[T]:
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
        height = height if height is not None else self.height

        for level in range(height, 0, -1):
            ix_i = self.slice_key(ix, level)

            if (child := node.children[ix_i]) is None:
                t_type = TrieLeafNode if level == 1 else TrieNode
                node.children.insert(ix_i, t_type(self.order, parent=node))
            else:
                node.children[ix_i] = child.copy() if not self.mutation else child

            node.children[ix_i].parent = node
            node = node.children[ix_i]

        return node

    def put(self, ix: int, value: T) -> "Trie[T]":
        def get_next_leaf() -> Tuple[TrieNode[T], TrieLeafNode[T]]:
            if ix == self.size and is_power_of(ix, b=self.order):
                root = TrieNode(
                    self.order, children=SparseList(self.order, data=[self.root])
                )
                return root, self.path_to(ix, root)
            else:
                root = self.root.copy() if not self.mutation else self.root
                return root, self.path_to(ix, root)

        root, node = get_next_leaf()
        node.values.insert(ix & self.mask, value)

        if self.mutation:
            self.root = root
            self.size += 1
            return self
        else:
            return self._create(root, self.size + 1)

    def append(self, *values: T) -> "Trie[T]":
        for value in values:
            self = self.put(self.size, value)
        return self

    def popitem(self, ix: int) -> "Trie[T]":
        root = self.root.copy() if not self.mutation else self.root
        height = self.get_tree_height(ix, self.order)

        if is_power_of(ix, b=self.order):
            root = root.children[0]
        else:
            node = self.path_to(ix, root, height)
            if ix & self.mask == 0:
                node.parent.children.pop(self.slice_key(ix, 1))
            else:
                node.values.pop(ix & self.mask)

        return self._create(root, self.size - 1)

    def pop(self) -> "Trie[T]":
        return self.popitem(self.size - 1)


if __name__ == "__main__":
    tree = Trie(4)
    tree0 = tree.append(0)
    tree1 = tree0.append(1, 2, 3)

    tree2 = tree1.append(4, 5, 6, 7, 8, 9)
    l1 = tree1.root.values
    l2 = tree2.root.children[0].values

    print(l1 is l2)

    tree3 = tree2.pop().pop().pop()
    tree3 = tree3.append(7)
    print("d")
