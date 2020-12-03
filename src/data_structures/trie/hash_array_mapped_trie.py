import math
from typing import *

from typing_extensions import *

from src.data_structures.utils.utils import is_power_of

__all__ = ["HashArrayMappedTrie", "Node", "WIDTH", "get_tree_depth"]

T = TypeVar("T")
S = TypeVar("S")

# Constants that define the shape of the tree structure.
# In production, BITS would likely be log_2(32) = 5, like that of Clojure's
# HashArrayMappedTrie implemenetation.

# Levels of the tree, also used to slice up a given index into
# the HashArrayMappedTrie into BITS intervals. So 4 = b0100 would be broken up into
# 01 and 00.
BITS = 2
# Width of the leaf nodes.
WIDTH = 1 << BITS
# Mask to slice up the aforesaid index, or key.
MASK = WIDTH - 1


class Node(Generic[T]):
    def __init__(self, children: Optional[List[Union[Optional[T], "Node[T]"]]] = None):
        if children is not None:
            self.children = children + [None] * (WIDTH - len(children))
        else:
            self.children = [None] * WIDTH

    def copy(self):
        return Node(list(self.children))


def get_tree_depth(length: int, node_size: int = WIDTH) -> int:
    return 0 if length == 0 else math.floor(math.log(length, node_size))


class HashArrayMappedTrie(Sequence[T]):
    def __init__(self, vals: List[T]):
        self.root: Node[T] = Node()
        self.length = 0
        self.mutation = False

        self.mutate()
        for val in vals:
            self.append(val)
        self.mutate()

    def __len__(self) -> int:
        return self.length

    @staticmethod
    def _create(root: Node[T], length: int) -> "HashArrayMappedTrie":
        out: "HashArrayMappedTrie[T]" = HashArrayMappedTrie([])
        out.root = root
        out.length = length
        return out

    @staticmethod
    def _reduce_node(
        key: int,
        reducer: Callable[[S, int, int], S],
        init: S,
        depth: int,
    ) -> S:
        """Low-level list reduction function.

        Args:
            key (int): leaf child key index. For example, if you wanted to grab the last element
            of an array of n elements, key = n.
            reducer (Callable[[S, int, int], S]): Reduction function that requires:
                a reducer value of type S,
                the current level in the tree **(0-indexed from the bottom up)**,
                a current index into said level.
            init (S): initial value to reduce upon.
            depth (Optional[int], optional): depth to traverse down to. Defaults to the list's max depth.

        Returns:
            S: the reduced value.
        """
        acc = init

        for level in range(depth, 0, -1):
            ix = (key >> (level * BITS)) & MASK
            acc = reducer(acc, level, ix)

        return acc

    def _at(self, key: int, func: Optional[Callable[[int, Node[T]], S]] = None) -> S:
        """Returns an element located at index `key`.
        Takes an optional callback func that must return a leaf node value.
        """
        leaf_ix = key & MASK
        func = (
            func
            if func is not None
            else lambda leaf_ix, leaf: cast(S, leaf.children[leaf_ix])
        )

        def reducer(node: Node[T], level: int, ix: int) -> Node[T]:
            return node.children[ix]

        leaf = self._reduce_node(key, reducer, self.root, get_tree_depth(self.length))

        return func(leaf_ix, leaf)

    def mutate(self) -> None:
        self.mutation = not self.mutation

    def append(self, val: T) -> "HashArrayMappedTrie":
        """There's 3 cases when appending, in order initial possibility:
        1. Root overflow: there's no more space in the entire tree: thus we must
        create an entirely new root, whereof's left branch is the current root.

        2. There's no room in the left branch, and the right branch is None: thus we must
        create a right branch and fill its first element with "value".

        3. There's space in the current branch: we simply insert "value" here,
        path copying on the way down.
        """
        root = self.root
        length = self.length + 1
        key = self.length
        leaf_ix = key & MASK

        # Case 1.
        if is_power_of(length, WIDTH):
            root = Node([root])

        root = root.copy() if not self.mutation else root

        def reducer(node: Node[T], level: int, ix: int) -> Node[T]:

            if (children := node.children[ix]) is None:
                # Case 2.
                node.children[ix] = Node()
            else:
                node.children[ix] = children.copy() if not self.mutation else children

            return node.children[ix]

        leaf = self._reduce_node(key, reducer, root, get_tree_depth(length))
        # Case 3.
        leaf.children[leaf_ix] = val

        if not self.mutation:
            return self._create(root, length)
        else:
            self.root = root
            self.length = length
            return self

    def pop(self) -> "HashArrayMappedTrie[T]":
        """There's 3 cases when popping, in order of initial possibility:
        1. Root underflow: the current length is a power of WIDTH, meaning our last call to
        `append` created a dead branch: we trim this off at the root and continue to case 3.

        2. The right-most leaf node is all "None"s after popping: we set this entire node to None.

        3. The right-most leaf node has at least one element in it: we simply set it to None.
        """
        root = self.root
        length = self.length - 1
        key = self.length - 1
        leaf_ix = key & MASK

        # Case 1.
        if is_power_of(self.length, WIDTH):
            root = root.children[0]

        root = root.copy() if not self.mutation else root

        def reducer(nodes: Tuple[Node[T], Node[T]], level: int, ix: int):
            prev_node, node = nodes
            children = node.children[ix]

            node.children[ix] = children.copy() if not self.mutation else children

            # Case 2.
            if level == 1 and leaf_ix == 0:
                node.children[ix] = None
                return node, None
            else:
                return node, node.children[ix]

        prev_leaf, leaf = self._reduce_node(
            key, reducer, (root, root), get_tree_depth(length)
        )

        # Case 3.
        if leaf is not None:
            leaf.children[leaf_ix] = None

        if not self.mutation:
            return self._create(root, length)
        else:
            self.root = root
            self.length = length
            return self

    @staticmethod
    def of(*args: S) -> "HashArrayMappedTrie[S]":
        return HashArrayMappedTrie(list(args))

    def copy(self) -> "HashArrayMappedTrie[T]":
        out = self.append(None)
        return out.pop()
